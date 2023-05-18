/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './trojstenid/**/*.{html,js}',
    ],
    theme: {
        extend: {},
    },
    variants: {
        extend: {},
    },
    plugins: [
        require('@tailwindcss/forms'),
    ],
}
