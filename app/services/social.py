"""Friends and friend duels between real players.

Duel state advances lazily — on every read — so no background worker is needed.
"""

import re
from datetime import datetime, timedelta

from app.core.clock import as_utc, new_id, utcnow
from app.core.errors import ConflictError, NotFoundError, UnprocessableError
from app.domain.economy import DUEL_STAKES, DUEL_START_GRACE_HOURS, DUEL_TIME_LIMITS, DUEL_WIN_BONUS
from app.repositories.catalog import ProblemRepository
from app.repositories.social import DuelRepository, FriendRequestRepository, FriendshipRepository
from app.repositories.users import UserRepository
from app.schemas.social import (
    AddFriendResult,
    DuelActionResult,
    DuelCreate,
    DuelDoc,
    DuelPlayerState,
    DuelStatus,
    DuelView,
    FriendRequestDoc,
    FriendRequestOutcome,
    FriendRequestView,
    SocialOverview,
)
from app.schemas.users import Player
from app.services.quests import ProgressTracker
from app.services.users import to_player
from app.services.wallet import WalletService

UUID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def decide_winner(duel: DuelDoc) -> str | None:
    """Faster solve wins; a solve beats no solve; equal times or no solves are a draw (None)."""
    a, b = duel.challenger_id, duel.opponent_id
    pa, pb = duel.players.get(a, DuelPlayerState()), duel.players.get(b, DuelPlayerState())
    if pa.solved and pb.solved:
        if pa.seconds == pb.seconds:
            return None
        return a if (pa.seconds or 0) < (pb.seconds or 0) else b
    if pa.solved:
        return a
    if pb.solved:
        return b
    return None


class SocialService:
    def __init__(self, users: UserRepository, requests: FriendRequestRepository, friendships: FriendshipRepository):
        self.users = users
        self.requests = requests
        self.friendships = friendships

    async def _players(self, ids: list[str]) -> dict[str, Player]:
        return {u.id: to_player(u) for u in await self.users.get_many(ids)}

    async def overview(self, user_id: str) -> SocialOverview:
        friend_ids = await self.friendships.friend_ids(user_id)
        incoming = await self.requests.pending(to_id=user_id)
        outgoing = await self.requests.pending(from_id=user_id)
        players = await self._players([*friend_ids, *(r.from_id for r in incoming), *(r.to_id for r in outgoing)])
        return SocialOverview(
            my_id=user_id,
            friends=[players[f] for f in friend_ids if f in players],
            incoming_requests=[
                FriendRequestView(player_id=r.from_id, player=players[r.from_id], at=r.created_at)
                for r in incoming
                if r.from_id in players
            ],
            outgoing_requests=[
                FriendRequestView(player_id=r.to_id, player=players[r.to_id], at=r.created_at)
                for r in outgoing
                if r.to_id in players
            ],
        )

    async def send_request(self, user_id: str, raw_player_id: str) -> FriendRequestOutcome:
        result = await self._send(user_id, raw_player_id.strip().lower())
        return FriendRequestOutcome(result=result, overview=await self.overview(user_id))

    async def _send(self, user_id: str, player_id: str) -> AddFriendResult:
        if not UUID_PATTERN.match(player_id):
            return "invalid"
        if player_id == user_id.lower():
            return "self"
        if not await self.users.get(player_id):
            return "not-found"
        if await self.friendships.are_friends(user_id, player_id):
            return "already-friends"
        if any(r.to_id == player_id for r in await self.requests.pending(from_id=user_id)):
            return "already-sent"
        if any(r.from_id == player_id for r in await self.requests.pending(to_id=user_id)):
            await self.accept(user_id, player_id)
            return "accepted-incoming"
        created = await self.requests.create(
            FriendRequestDoc(id=new_id(), from_id=user_id, to_id=player_id, created_at=utcnow())
        )
        return "sent" if created else "already-sent"

    async def accept(self, user_id: str, player_id: str) -> SocialOverview:
        now = utcnow()
        if not await self.requests.resolve(player_id, user_id, "accepted", now):
            raise NotFoundError("No pending request from that player.")
        await self.friendships.add(user_id, player_id, now)
        return await self.overview(user_id)

    async def decline(self, user_id: str, player_id: str) -> SocialOverview:
        if not await self.requests.resolve(player_id, user_id, "declined", utcnow()):
            raise NotFoundError("No pending request from that player.")
        return await self.overview(user_id)

    async def cancel_request(self, user_id: str, player_id: str) -> SocialOverview:
        if not await self.requests.resolve(user_id, player_id, "cancelled", utcnow()):
            raise NotFoundError("No pending request to that player.")
        return await self.overview(user_id)

    async def remove_friend(self, user_id: str, player_id: str) -> SocialOverview:
        if not await self.friendships.remove(user_id, player_id):
            raise NotFoundError("That player isn't your friend.")
        return await self.overview(user_id)


class DuelService:
    def __init__(
        self,
        duels: DuelRepository,
        users: UserRepository,
        friendships: FriendshipRepository,
        problems: ProblemRepository,
        wallet: WalletService,
        tracker: ProgressTracker,
    ):
        self.duels = duels
        self.users = users
        self.friendships = friendships
        self.problems = problems
        self.wallet = wallet
        self.tracker = tracker

    # --- Views ---------------------------------------------------------------------------
    @staticmethod
    def view(duel: DuelDoc, me: str, friend: Player | None = None) -> DuelView:
        friend_id = duel.opponent_id if duel.challenger_id == me else duel.challenger_id
        mine = duel.players.get(me, DuelPlayerState())
        theirs = duel.players.get(friend_id, DuelPlayerState())
        my_finished = mine.finished_at is not None
        status: DuelStatus
        if duel.status == "finished":
            status = "draw" if duel.winner_id is None else ("won" if duel.winner_id == me else "lost")
        else:
            status = duel.status
        return DuelView(
            id=duel.id,
            friend_id=friend_id,
            friend=friend,
            problem_slug=duel.problem_slug,
            time_limit_minutes=duel.time_limit_minutes,
            stake=duel.stake,
            direction="sent" if duel.challenger_id == me else "received",
            created_at=duel.created_at,
            started_at=mine.started_at,
            finished_at=mine.finished_at,
            my_finished=my_finished,
            my_seconds=mine.seconds if mine.solved else None,
            # Only revealed once my own result is in.
            friend_seconds=theirs.seconds if my_finished and theirs.solved else None,
            status=status,
        )

    async def _view(self, duel: DuelDoc, me: str) -> DuelView:
        other = duel.opponent_id if duel.challenger_id == me else duel.challenger_id
        friend = await self.users.get(other)
        return self.view(duel, me, to_player(friend) if friend else None)

    async def _get_mine(self, user_id: str, duel_id: str) -> DuelDoc:
        duel = await self.duels.get(duel_id)
        if not duel or user_id not in (duel.challenger_id, duel.opponent_id):
            raise NotFoundError("Duel not found.")
        return await self._advance(duel)

    async def list_duels(self, user_id: str) -> list[DuelView]:
        duels = [await self._advance(d) for d in await self.duels.for_user(user_id)]
        others = {d.opponent_id if d.challenger_id == user_id else d.challenger_id for d in duels}
        players = {u.id: to_player(u) for u in await self.users.get_many(list(others))}
        return [
            self.view(d, user_id, players.get(d.opponent_id if d.challenger_id == user_id else d.challenger_id))
            for d in duels
        ]

    async def get(self, user_id: str, duel_id: str) -> DuelView:
        return await self._view(await self._get_mine(user_id, duel_id), user_id)

    # --- Lazy state machine ------------------------------------------------------------------
    async def _advance(self, duel: DuelDoc) -> DuelDoc:
        now = utcnow()
        if duel.status == "active":
            duel = await self._expire_players(duel, now)
            if all(duel.players.get(p, DuelPlayerState()).finished_at for p in (duel.challenger_id, duel.opponent_id)):
                duel = await self._settle(duel)
        return duel

    async def _expire_players(self, duel: DuelDoc, now: datetime) -> DuelDoc:
        limit = timedelta(minutes=duel.time_limit_minutes)
        for player_id in (duel.challenger_id, duel.opponent_id):
            state = duel.players.get(player_id, DuelPlayerState())
            if state.finished_at:
                continue
            started = as_utc(state.started_at) if state.started_at else None
            accepted = as_utc(duel.accepted_at) if duel.accepted_at else as_utc(duel.created_at)
            expired = (started and now >= started + limit) or (
                not started and now >= accepted + timedelta(hours=DUEL_START_GRACE_HOURS)
            )
            if expired:
                duel = (
                    await self.duels.set_player_fields(
                        duel.id,
                        player_id,
                        {"finished_at": now, "seconds": None, "solved": False},
                        only_if_unset="finished_at",
                    )
                    or await self.duels.get(duel.id)
                    or duel
                )
        return duel

    async def _settle(self, duel: DuelDoc) -> DuelDoc:
        winner = decide_winner(duel)
        settled = await self.duels.claim_settlement(duel.id, winner)
        if not settled:  # someone else settled it first
            return await self.duels.get(duel.id) or duel
        players = (duel.challenger_id, duel.opponent_id)
        for player_id in players:
            await self.users.inc_stats(
                player_id, {"duels_played": 1, **({"duels_won": 1} if player_id == winner else {})}
            )
        if winner:
            if duel.stake:
                await self.wallet.credit(winner, duel.stake * 2, "Duel won — both stakes")
            await self.wallet.earn(
                winner,
                DUEL_WIN_BONUS,
                "Duel win bonus",
                reward_key=f"duel:{duel.id}",
                activity="won a friend duel",
                sprite="sword",
            )
            await self.tracker.record(winner, "duel_won")
        elif duel.stake:
            for player_id in players:
                await self.wallet.credit(player_id, duel.stake, "Duel draw — stake refunded")
        return settled

    # --- Actions ---------------------------------------------------------------------------------
    async def create(self, user_id: str, body: DuelCreate) -> DuelActionResult:
        friend_id = body.friend_id.strip().lower()
        if body.stake not in DUEL_STAKES:
            raise UnprocessableError(f"Stake must be one of {', '.join(map(str, DUEL_STAKES))} XP.")
        if body.time_limit_minutes not in DUEL_TIME_LIMITS:
            raise UnprocessableError(f"Time limit must be one of {', '.join(map(str, DUEL_TIME_LIMITS))} minutes.")
        if not await self.friendships.are_friends(user_id, friend_id):
            raise ConflictError("You can only duel your friends.")
        if not await self.problems.by_slug(body.problem_slug):
            raise NotFoundError("Problem not found.")
        balance = (
            await self.wallet.spend(user_id, body.stake, "Duel stake")
            if body.stake
            else await self.wallet.balance(user_id)
        )
        duel = DuelDoc(
            id=new_id(),
            challenger_id=user_id,
            opponent_id=friend_id,
            problem_slug=body.problem_slug,
            time_limit_minutes=body.time_limit_minutes,
            stake=body.stake,
            created_at=utcnow(),
        )
        await self.duels.insert(duel)
        return DuelActionResult(duel=await self._view(duel, user_id), balance=balance)

    async def accept(self, user_id: str, duel_id: str) -> DuelActionResult:
        duel = await self._get_mine(user_id, duel_id)
        if duel.opponent_id != user_id or duel.status != "pending":
            raise ConflictError("This duel can't be accepted.")
        if duel.stake:
            await self.wallet.spend(user_id, duel.stake, "Duel stake")
        updated = await self.duels.transition(duel.id, "pending", {"status": "active", "accepted_at": utcnow()})
        if not updated:
            if duel.stake:
                await self.wallet.credit(user_id, duel.stake, "Duel no longer pending — stake refunded")
            raise ConflictError("This duel is no longer pending.")
        return DuelActionResult(duel=await self._view(updated, user_id), balance=await self.wallet.balance(user_id))

    async def decline(self, user_id: str, duel_id: str) -> DuelActionResult:
        duel = await self._get_mine(user_id, duel_id)
        if duel.opponent_id != user_id:
            raise ConflictError("Only the challenged player can decline.")
        updated = await self.duels.transition(duel.id, "pending", {"status": "declined"})
        if not updated:
            raise ConflictError("This duel is no longer pending.")
        if duel.stake:
            await self.wallet.credit(duel.challenger_id, duel.stake, "Duel declined — stake refunded")
        return DuelActionResult(duel=await self._view(updated, user_id), balance=await self.wallet.balance(user_id))

    async def cancel(self, user_id: str, duel_id: str) -> DuelActionResult:
        """The challenger can withdraw while the duel is pending, or active but not yet started by anyone."""
        duel = await self._get_mine(user_id, duel_id)
        if duel.challenger_id != user_id:
            raise ConflictError("Only the challenger can cancel.")
        i_started = bool(duel.players.get(user_id, DuelPlayerState()).started_at)
        they_started = bool(duel.players.get(duel.opponent_id, DuelPlayerState()).started_at)
        cancellable = duel.status == "pending" or (duel.status == "active" and not i_started and not they_started)
        if not cancellable:
            raise ConflictError("This duel can't be cancelled anymore.")
        updated = await self.duels.transition(duel.id, duel.status, {"status": "cancelled"})
        if not updated:
            raise ConflictError("This duel changed — try again.")
        if duel.stake:
            await self.wallet.credit(duel.challenger_id, duel.stake, "Duel cancelled — stake refunded")
            if duel.status == "active":
                await self.wallet.credit(duel.opponent_id, duel.stake, "Duel cancelled — stake refunded")
        return DuelActionResult(duel=await self._view(updated, user_id), balance=await self.wallet.balance(user_id))

    async def start(self, user_id: str, duel_id: str) -> DuelView:
        """Opens my board: my clock starts now (idempotent)."""
        duel = await self._get_mine(user_id, duel_id)
        if duel.status != "active":
            raise ConflictError("This duel isn't active.")
        updated = await self.duels.set_player_fields(
            duel.id, user_id, {"started_at": utcnow()}, only_if_unset="started_at"
        )
        return await self._view(updated or await self._get_mine(user_id, duel_id), user_id)

    async def record_solve(self, user_id: str, duel_id: str, problem_slug: str) -> DuelView:
        """Called when the player's Submit passes on the duel's problem. The server times it."""
        duel = await self._get_mine(user_id, duel_id)
        if duel.problem_slug != problem_slug:
            raise UnprocessableError("That submission is for a different problem than the duel.")
        mine = duel.players.get(user_id, DuelPlayerState())
        if duel.status == "active" and mine.started_at and not mine.finished_at:
            now = utcnow()
            seconds = int((now - as_utc(mine.started_at)).total_seconds())
            solved = seconds <= duel.time_limit_minutes * 60
            await self.duels.set_player_fields(
                duel.id,
                user_id,
                {"finished_at": now, "seconds": seconds if solved else None, "solved": solved},
                only_if_unset="finished_at",
            )
        return await self._view(await self._get_mine(user_id, duel_id), user_id)

    async def forfeit(self, user_id: str, duel_id: str) -> DuelView:
        """Gives up (or the board's clock ran out): scored as not solved."""
        duel = await self._get_mine(user_id, duel_id)
        if duel.status != "active":
            raise ConflictError("This duel isn't active.")
        await self.duels.set_player_fields(
            duel.id, user_id, {"finished_at": utcnow(), "seconds": None, "solved": False}, only_if_unset="finished_at"
        )
        return await self._view(await self._get_mine(user_id, duel_id), user_id)
