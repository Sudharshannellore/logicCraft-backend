// A small, dependency-free implementation of the Jest API that Exercism's JavaScript and TypeScript
// tests use: describe/test/it (and their x- variants, which Exercism runs too), hooks, `expect` with
// the common matchers, `.not`/`.resolves`/`.rejects`, asymmetric matchers and `expect.extend`.
// Specs import it as '@jest/globals'. `run()` executes the collected tests and reports each result
// on its own line, so results survive even if a later test hangs.

import { inspect } from 'node:util'

const MARKER = '__LOGICRAFT_TEST__'
const block = (name, parent = null) => ({ name, parent, children: [], beforeEach: [], afterEach: [], beforeAll: [], afterAll: [] })
const root = block('')
let current = root

export function describe(name, fn) {
  const child = block(String(name), current)
  current.children.push(child)
  const previous = current
  current = child
  try {
    fn()
  } finally {
    current = previous
  }
}
describe.skip = describe
describe.only = describe
export const xdescribe = describe
export const fdescribe = describe

export function test(name, fn) {
  current.children.push({ test: true, name: String(name), fn })
}
test.skip = test
test.only = test
test.todo = () => {}
export const it = test
export const xtest = test
export const xit = test
export const fit = test

export const beforeEach = (fn) => current.beforeEach.push(fn)
export const afterEach = (fn) => current.afterEach.push(fn)
export const beforeAll = (fn) => current.beforeAll.push(fn)
export const afterAll = (fn) => current.afterAll.push(fn)

// --- Equality -------------------------------------------------------------------------------------

const isAsymmetric = (value) => value !== null && typeof value === 'object' && typeof value.asymmetricMatch === 'function'
const tag = (value) => Object.prototype.toString.call(value)

export function equals(a, b, strict = false) {
  if (isAsymmetric(b)) return b.asymmetricMatch(a)
  if (isAsymmetric(a)) return a.asymmetricMatch(b)
  if (Object.is(a, b)) return true
  if (a === null || b === null || typeof a !== 'object' || typeof b !== 'object') return false
  if (tag(a) !== tag(b)) return false
  if (strict && Object.getPrototypeOf(a) !== Object.getPrototypeOf(b)) return false
  if (a instanceof Date) return a.getTime() === b.getTime()
  if (a instanceof RegExp) return String(a) === String(b)
  if (a instanceof Error && !(strict)) return a.message === b.message
  if (a instanceof Map) {
    if (a.size !== b.size) return false
    for (const [key, value] of a) {
      if (b.has(key)) {
        if (!equals(value, b.get(key), strict)) return false
      } else if (![...b].some(([k, v]) => equals(key, k, strict) && equals(value, v, strict))) return false
    }
    return true
  }
  if (a instanceof Set) {
    if (a.size !== b.size) return false
    for (const value of a) if (!b.has(value) && ![...b].some((v) => equals(value, v, strict))) return false
    return true
  }
  if (ArrayBuffer.isView(a)) return a.length === b.length && [...a].every((v, i) => Object.is(v, b[i]))
  if (Array.isArray(a)) {
    if (a.length !== b.length) return false
    for (let i = 0; i < a.length; i++) {
      if (strict && (i in a) !== (i in b)) return false
      if (!equals(a[i], b[i], strict)) return false
    }
  }
  // toEqual ignores properties whose value is undefined; toStrictEqual does not.
  const keys = (o) => Object.keys(o).filter((k) => strict || o[k] !== undefined)
  const ka = keys(a)
  const kb = keys(b)
  if (ka.length !== kb.length) return false
  return ka.every((k) => Object.prototype.hasOwnProperty.call(b, k) && equals(a[k], b[k], strict))
}

// --- Matchers ----------------------------------------------------------------------------------

const show = (value) => (isAsymmetric(value) ? value.toString() : inspect(value, { depth: 6, breakLength: 100, maxArrayLength: 50 }))

class AssertionError extends Error {}

function thrownBy(received, fromPromise) {
  if (fromPromise) return { threw: true, error: received }
  if (typeof received !== 'function') throw new AssertionError('expect(received).toThrow() needs a function to call')
  try {
    received()
    return { threw: false }
  } catch (error) {
    return { threw: true, error }
  }
}

function throwMatches(error, expected) {
  if (expected === undefined) return true
  const message = error && typeof error === 'object' && 'message' in error ? String(error.message) : String(error)
  if (typeof expected === 'string') return message.includes(expected)
  if (expected instanceof RegExp) return expected.test(message)
  if (typeof expected === 'function') return error instanceof expected
  if (expected instanceof Error || (expected && typeof expected === 'object' && 'message' in expected)) return message === expected.message
  return equals(error, expected)
}

const builtins = {
  toBe: (r, e) => [Object.is(r, e), () => `Expected: ${show(e)}\nReceived: ${show(r)}`],
  toEqual: (r, e) => [equals(r, e), () => `Expected: ${show(e)}\nReceived: ${show(r)}`],
  toStrictEqual: (r, e) => [equals(r, e, true), () => `Expected: ${show(e)}\nReceived: ${show(r)}`],
  toBeTruthy: (r) => [!!r, () => `Received: ${show(r)}`],
  toBeFalsy: (r) => [!r, () => `Received: ${show(r)}`],
  toBeNull: (r) => [r === null, () => `Received: ${show(r)}`],
  toBeUndefined: (r) => [r === undefined, () => `Received: ${show(r)}`],
  toBeDefined: (r) => [r !== undefined, () => `Received: ${show(r)}`],
  toBeNaN: (r) => [Number.isNaN(r), () => `Received: ${show(r)}`],
  toBeCloseTo: (r, e, digits = 2) => [
    Math.abs(e - r) < 10 ** -digits / 2,
    () => `Expected: ${show(e)} (to ${digits} decimal places)\nReceived: ${show(r)}`,
  ],
  toBeGreaterThan: (r, e) => [r > e, () => `Expected: > ${show(e)}\nReceived: ${show(r)}`],
  toBeGreaterThanOrEqual: (r, e) => [r >= e, () => `Expected: >= ${show(e)}\nReceived: ${show(r)}`],
  toBeLessThan: (r, e) => [r < e, () => `Expected: < ${show(e)}\nReceived: ${show(r)}`],
  toBeLessThanOrEqual: (r, e) => [r <= e, () => `Expected: <= ${show(e)}\nReceived: ${show(r)}`],
  toBeInstanceOf: (r, e) => [r instanceof e, () => `Expected an instance of ${e && e.name}\nReceived: ${show(r)}`],
  toMatch: (r, e) => [
    typeof r === 'string' && (e instanceof RegExp ? e.test(r) : r.includes(e)),
    () => `Expected to match: ${show(e)}\nReceived: ${show(r)}`,
  ],
  toHaveLength: (r, e) => [r != null && r.length === e, () => `Expected length: ${e}\nReceived length: ${r == null ? r : r.length}`],
  toContain: (r, e) => [
    r != null && (typeof r === 'string' ? r.includes(e) : [...r].includes(e)),
    () => `Expected to contain: ${show(e)}\nReceived: ${show(r)}`,
  ],
  toContainEqual: (r, e) => [r != null && [...r].some((v) => equals(v, e)), () => `Expected to contain: ${show(e)}\nReceived: ${show(r)}`],
  toHaveProperty: (r, path, value) => {
    const parts = Array.isArray(path) ? path : String(path).split('.')
    let target = r
    for (const p of parts) {
      if (target == null || !(p in Object(target))) return [false, () => `Expected property: ${show(path)}\nReceived: ${show(r)}`]
      target = target[p]
    }
    return [value === undefined || equals(target, value), () => `Expected ${show(path)} to be ${show(value)}\nReceived: ${show(target)}`]
  },
}

const custom = {}

function makeExpect(received, { negate = false, promise = null } = {}) {
  const matchers = {}
  const names = new Set([...Object.keys(builtins), ...Object.keys(custom), 'toThrow', 'toThrowError'])
  for (const name of names) {
    const check = (actual, args) => {
      let pass
      let message
      if (name === 'toThrow' || name === 'toThrowError') {
        const outcome = thrownBy(actual, promise === 'rejects')
        pass = outcome.threw && throwMatches(outcome.error, args[0])
        message = () =>
          outcome.threw
            ? `Expected the error to match: ${show(args[0])}\nThrown: ${show(outcome.error && outcome.error.message !== undefined ? outcome.error.message : outcome.error)}`
            : 'Expected the function to throw an error, but it did not throw.'
      } else if (name in custom) {
        const result = custom[name].call(
          { isNot: negate, promise: promise ?? '', equals, utils: { printReceived: show, printExpected: show, matcherHint: () => '', stringify: show } },
          actual,
          ...args,
        )
        pass = result.pass
        message = result.message
      } else {
        ;[pass, message] = builtins[name](actual, ...args)
      }
      if (pass === negate) {
        throw new AssertionError(`expect(received).${negate ? 'not.' : ''}${name}(${args.length ? 'expected' : ''})\n\n${message()}`)
      }
    }
    matchers[name] = (...args) => {
      if (promise === null) return check(received, args)
      return Promise.resolve(received).then(
        (value) => {
          if (promise === 'rejects') throw new AssertionError(`Expected the promise to reject, but it resolved to ${show(value)}`)
          return check(value, args)
        },
        (error) => {
          if (promise === 'resolves') throw new AssertionError(`Expected the promise to resolve, but it rejected with ${show(error && error.message !== undefined ? error.message : error)}`)
          return check(error, args)
        },
      )
    }
  }
  return matchers
}

export function expect(received) {
  const matchers = makeExpect(received)
  matchers.not = makeExpect(received, { negate: true })
  matchers.resolves = makeExpect(received, { promise: 'resolves' })
  matchers.resolves.not = makeExpect(received, { negate: true, promise: 'resolves' })
  matchers.rejects = makeExpect(received, { promise: 'rejects' })
  matchers.rejects.not = makeExpect(received, { negate: true, promise: 'rejects' })
  return matchers
}

const asymmetric = (description, match) => ({ asymmetricMatch: match, toString: () => description, [inspect.custom]: () => description })
expect.extend = (matchers) => Object.assign(custom, matchers)
expect.anything = () => asymmetric('Anything', (v) => v !== null && v !== undefined)
expect.any = (ctor) =>
  asymmetric(`Any<${ctor && ctor.name}>`, (v) =>
    ctor === Number ? typeof v === 'number' || v instanceof Number
      : ctor === String ? typeof v === 'string' || v instanceof String
        : ctor === Boolean ? typeof v === 'boolean' || v instanceof Boolean
          : ctor === Function ? typeof v === 'function'
            : v instanceof ctor,
  )
expect.objectContaining = (object) =>
  asymmetric(`ObjectContaining ${show(object)}`, (v) => v !== null && typeof v === 'object' && Object.keys(object).every((k) => k in v && equals(v[k], object[k])))
expect.arrayContaining = (array) => asymmetric(`ArrayContaining ${show(array)}`, (v) => Array.isArray(v) && array.every((e) => v.some((x) => equals(x, e))))
expect.stringContaining = (text) => asymmetric(`StringContaining ${show(text)}`, (v) => typeof v === 'string' && v.includes(text))
expect.stringMatching = (pattern) =>
  asymmetric(`StringMatching ${show(pattern)}`, (v) => typeof v === 'string' && (pattern instanceof RegExp ? pattern.test(v) : v.includes(pattern)))
expect.assertions = () => {}
expect.hasAssertions = () => {}

export const jest = { fn: () => () => {}, setTimeout: () => {} }

// --- Runner -----------------------------------------------------------------------------------

const TEST_TIMEOUT_MS = 5000
const report = (result) => process.stdout.write(`\n${MARKER}${JSON.stringify(result)}\n`)

function describeError(error) {
  if (error instanceof AssertionError) return error.message
  const name = error && error.constructor && error.constructor.name ? error.constructor.name : 'Error'
  const message = error && error.message !== undefined ? error.message : String(error)
  // Point at the learner's line when the error came from their file.
  const frame = error && typeof error.stack === 'string' ? error.stack.split('\n').find((l) => /\.(m?js|ts):\d+/.test(l) && !/jest\.mjs|\.(spec|test)\./.test(l)) : null
  const where = frame ? frame.match(/([\w.-]+\.(?:m?js|ts)):(\d+)/) : null
  return `${name}: ${message}${where ? ` (${where[1]} line ${where[2]})` : ''}`
}

function withTimeout(promise) {
  let timer
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      timer = setTimeout(() => reject(new AssertionError(`Test timed out after ${TEST_TIMEOUT_MS / 1000}s`)), TEST_TIMEOUT_MS)
    }),
  ]).finally(() => clearTimeout(timer))
}

async function walk(node, names, befores, afters) {
  for (const hook of node.beforeAll) await hook()
  for (const child of node.children) {
    if (child.test) {
      const name = [...names, child.name].join(' › ')
      try {
        for (const hook of [...befores, ...node.beforeEach]) await hook()
        await withTimeout(Promise.resolve().then(() => child.fn()))
        report({ name, status: 'pass' })
      } catch (error) {
        report({ name, status: error instanceof AssertionError ? 'fail' : 'error', message: describeError(error) })
      } finally {
        for (const hook of [...node.afterEach, ...afters]) {
          try {
            await hook()
          } catch {
            // an afterEach failure shouldn't hide the test's own result
          }
        }
      }
    } else {
      await walk(child, [...names, child.name], [...befores, ...node.beforeEach], [...node.afterEach, ...afters])
    }
  }
  for (const hook of node.afterAll) await hook()
}

export async function run() {
  await walk(root, [], [], [])
}
