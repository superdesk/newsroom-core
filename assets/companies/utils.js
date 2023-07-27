
export function getCountryLabel(code, _countries) {
    return (_countries.find(c => c.value === code) || {}).text;
}

export function isProductEnabled(products, productId) {
    return products.findIndex((product) => product._id === productId) !== -1;
}
