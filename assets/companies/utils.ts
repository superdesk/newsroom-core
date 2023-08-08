
export function getCountryLabel(code: any, _countries: any) {
    return (_countries.find((c: any) => c.value === code) || {}).text;
}

export function isProductEnabled(products: any, productId: any) {
    return products.findIndex((product: any) => product._id === productId) !== -1;
}
