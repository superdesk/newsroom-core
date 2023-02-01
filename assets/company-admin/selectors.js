import {createSelector} from 'reselect';

export const sectionListSelector = (state) => state.sections;

export const productListSelector = (state) => state.products;
export const productIdMapSelector = createSelector(
    [productListSelector],
    (productList) => (
        productList.reduce((products, product) => {
            products[product._id] = product;

            return products;
        }, {})
    )
);
export const companyListSelector = (state) => state.companies;

export const companySectionListSelector = createSelector(
    [sectionListSelector, companyListSelector],
    (sectionList, companyList) => (
        companyList.reduce((companySections, company) => {
            companySections[company._id] = sectionList.filter(
                (section) => (
                    company.sections[section._id] === true
                )
            );

            return companySections;
        }, {})
    )
);

export const currentUserSelector = (state) => state.user;
export const userIdSelector = (state) => state.users;
export const userIdMapSelector = (state) => state.usersById;

export const currentCompanySelector = createSelector(
    [currentUserSelector, companyListSelector],
    (user, companyList) => (
        companyList.find((company) => company._id === user.company)
    )
);

export const companyUserListSelector = createSelector(
    [companyListSelector, userIdMapSelector],
    (companyList, userMap) => (
        companyList.reduce((companyUsers, company) => {
            companyUsers[company._id] = Object
                .values(userMap)
                .filter((user) => user.company === company._id);

            return companyUsers;
        }, {})
    )
);

export const companyProductsSelector = createSelector(
    [companyListSelector, productListSelector],
    (companyList, productList) => (
        companyList.reduce((companyProducts, company) => {
            const companyProductIds = company.products.map(
                (product) => product._id
            );
            companyProducts[company._id] = productList.filter(
                (product) => companyProductIds.includes(product._id)
            );

            return companyProducts;
        }, {})
    )
);

export const companyProductSeatsSelector = createSelector(
    [companyListSelector, companyUserListSelector, productIdMapSelector],
    (companyList, companyUserList, productMap) => (
        companyList.reduce((companyProducts, company) => {
            companyProducts[company._id] = company.products.reduce(
                (productSeats, companyProduct) => {
                    const userSeats = companyUserList[company._id].filter(
                        (user) => user.products.some(
                            (userProduct) => userProduct._id === companyProduct._id
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
