import { awardSmoothScroll } from './components/smooth-scroll.js';
import { initFigureHover } from './components/figure-hover.js';

const CONFIG = { threshold: 64, beats: [[0, 0.2], [0.5, 0.8], [1, 1]] };

document.addEventListener('DOMContentLoaded', () => {
  awardSmoothScroll.init(document.body, CONFIG);
  initFigureHover(document.querySelectorAll('[data-figure]'));
  document.documentElement.classList.add('js-ready');
});

addEventListener('resize', () => {
  document.body.dataset.width = String(innerWidth);
});
