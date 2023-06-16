import {createSelector} from 'reselect';

export const sectionListSelector = (state: any) => state.sections || [];

export const productListSelector = (state: any) => state.products || [];
export const productIdMapSelector = createSelector(
    [productListSelector],
    (productList: any) => (
        productList.reduce((products: any, product: any) => {
            products[product._id] = product;

            return products;
        }, {})
    )
);
export const companyListSelector = (state: any) => state.companies || [];

export const companySectionListSelector = createSelector(
    [sectionListSelector, companyListSelector],
    (sectionList: any, companyList: any) => (
        companyList.reduce((companySections: any, company: any) => {
            companySections[company._id] = sectionList.filter(
                (section: any) => (
                    (company.sections || {})[section._id] === true
                )
            );

            return companySections;
        }, {})
    )
);

export const currentUserSelector = (state: any) => state.user || {};
export const userIdSelector = (state: any) => state.users || [];
export const userIdMapSelector = (state: any) => state.usersById || {};

export const currentCompanySelector = createSelector(
    [currentUserSelector, companyListSelector],
    (user: any, companyList: any) => (
        companyList.find((company: any) => company._id === user.company) || {}
    )
);

export const currentCompanySectionListSelector = createSelector(
    [currentCompanySelector, companySectionListSelector],
    (currentCompany: any, companySectionMap: any) => (
        companySectionMap[currentCompany._id] || []
    )
);

export const companyUserListSelector = createSelector(
    [companyListSelector, userIdMapSelector],
    (companyList: any, userMap: any) => (
        companyList.reduce((companyUsers: any, company: any) => {
            companyUsers[company._id] = Object
                .values(userMap)
                .filter((user: any) => user.company === company._id);

            return companyUsers;
        }, {})
    )
);

export const companyProductsSelector = createSelector(
    [companyListSelector, productListSelector],
    (companyList: any, productList: any) => (
        companyList.reduce((companyProducts: any, company: any) => {
            const companyProductIds = (company.products || []).map(
                (product: any) => product._id
            );
            companyProducts[company._id] = productList.filter(
                (product: any) => companyProductIds.includes(product._id)
            );

            return companyProducts;
        }, {})
    )
);

export const companyProductSeatsSelector = createSelector(
    [companyListSelector, companyUserListSelector, productIdMapSelector],
    (companyList: any, companyUserList: any, productMap: any) => (
        companyList.reduce((companyProducts: any, company: any) => {
            companyProducts[company._id] = (company.products || []).reduce(
                (productSeats: any, companyProduct: any) => {
                    const userSeats = companyUserList[company._id].filter(
                        (user: any) => (user.products || []).some(
                            (userProduct: any) => userProduct._id === companyProduct._id
                        )
                    );
                    productSeats[companyProduct._id] = {
                        _id: productMap[companyProduct._id]._id,
                        name: productMap[companyProduct._id].name,
                        description: productMap[companyProduct._id].description,
                        section: productMap[companyProduct._id].product_type,
                        max_seats: companyProduct.seats,
                        assigned_seats: userSeats.length,
                        max_reached: userSeats.length >= companyProduct.seats
                    };

                    return productSeats;
                },
                {}
            );

            return companyProducts;
        }, {})
    )
);
