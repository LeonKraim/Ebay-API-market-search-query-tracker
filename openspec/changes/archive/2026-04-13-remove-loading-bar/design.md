# Design: Remove Loading Bar

Remove all NProgress integration:
1. Strip `import NProgress from 'nprogress'` and the two NProgress calls from `client.ts`
2. Remove the `#nprogress` CSS blocks from `index.css`
3. Delete `TopLoadingBar.tsx` (exported but never imported anywhere)
