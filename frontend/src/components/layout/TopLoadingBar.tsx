/**
 * NProgress top loading bar — mounts once and is driven by the API client.
 * No props needed; NProgress is a global singleton.
 */
import { useEffect } from 'react'
import NProgress from 'nprogress'

NProgress.configure({
  showSpinner: false,
  trickleSpeed: 200,
  minimum: 0.08,
  easing: 'ease',
  speed: 400,
})

export function TopLoadingBar() {
  useEffect(() => {
    // Inject NProgress CSS once
    const id = 'nprogress-style'
    if (document.getElementById(id)) return
    const style = document.createElement('style')
    style.id = id
    style.textContent = `
      #nprogress { pointer-events: none; }
      #nprogress .bar {
        background: #3b82f6;
        position: fixed; z-index: 9999;
        top: 0; left: 0;
        width: 100%; height: 3px;
      }
      #nprogress .peg {
        display: block; position: absolute;
        right: 0; width: 100px; height: 100%;
        box-shadow: 0 0 10px #3b82f6, 0 0 5px #3b82f6;
        opacity: 1; transform: rotate(3deg) translate(0, -4px);
      }
    `
    document.head.appendChild(style)
  }, [])

  return null // rendered for side-effects only
}
