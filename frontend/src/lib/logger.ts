/**
 * Tiny client-side logger.
 * In production logs are silenced below WARN.
 */
const isDev = import.meta.env.DEV

const noop = () => {}

export const logger = {
  debug: isDev ? console.debug.bind(console, '[DEBUG]') : noop,
  info:  isDev ? console.info.bind(console,  '[INFO] ') : noop,
  warn:  console.warn.bind(console,  '[WARN] '),
  error: console.error.bind(console, '[ERROR]'),
}
