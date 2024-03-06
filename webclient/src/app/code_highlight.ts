import hljs from "highlight.js";

declare global {
  interface Window {
    hljs: typeof hljs;
  }
}

