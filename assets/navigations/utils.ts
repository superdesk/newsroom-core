/**
 * Returns the comma separated list of product types used for a given navigation
 * @param navigation
 * @param products
 * @returns {string}
 */
export function getProductTypes(navigation: any, products: any): any {
    if (!navigation || !products) {
        return '';
    }

    const productTypes: any = {};
    products.filter((product: any) => (product.navigations || []).includes(navigation._id)).forEach((p: any) =>
        p.product_type ? productTypes[p.product_type] = 1 : productTypes['wire'] = 1
    );

    return Object.keys(productTypes).join(', ');
}