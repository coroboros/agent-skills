/* Legal wiring: the frame tier map is data — paths resolve from the build root. */
var FRAME_TIERS = { hi: 'assets/frames/hi/' };
function frameUrl(tier, index) {
  return FRAME_TIERS[tier] + 'f_' + String(index).padStart(3, '0') + '.webp';
}
