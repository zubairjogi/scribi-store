module.exports = {
  content: [
    '../../templates/**/*.html',
    '../../store/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'), // remove if not using daisyUI
  ],
}
