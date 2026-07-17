import * as THREE from 'three';

const renderer = new THREE.WebGLRenderer({ antialias: true });
const frag = 'void main(){ gl_FragColor = vec4(1.0); }';

const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
ctx.drawImage(poster, 0, 0);

addEventListener('pointermove', onPointer);
const io = new IntersectionObserver(update);

function tick(t) {
  stage.style.transform = 'translateY(' + t + 'px)';
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);
