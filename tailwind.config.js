/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './trojstenid/**/*.{html,js}',
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['"Source Sans Pro"', 'sans-serif'],
            },
            colors: {
                trojsten: "#1077C1",
            }
        },
    },
    variants: {
        extend: {},
    },
    plugins: [
        require('@tailwindcss/forms'),
    ],
}
