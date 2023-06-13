import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';

import {gettext} from 'utils';

import {
    setError,
    saveCompanies,
    fetchCompanies,
    fetchNavigations,
    saveNavigations,
    postProduct,
    editProduct,
    selectProduct,
    deleteProduct,
    newProduct,
    cancelEdit
} from '../actions';

import {sectionsPropType} from 'features/sections/types';
import {sectionsSelector} from 'features/sections/selectors';
import {searchQuerySelector} from 'search/selectors';

import EditProduct from './EditProduct';
import ProductList from './ProductList';

import SearchResults from 'search/components/SearchResults';

class Products extends React.Component<any, any> {
    constructor(props: any, context: any) {
        super(props, context);

        this.isFormValid = this.isFormValid.bind(this);
        this.save = this.save.bind(this);
        this.deleteProduct = this.deleteProduct.bind(this);
    }

    isFormValid() {
        let valid = true;
        let errors: any = {};

        if (!this.props.productToEdit.name) {
            errors.name = [gettext('Please provide product name')];
            valid = false;
        }

        this.props.dispatch(setError(errors));
        return valid;
    }

    save(event: any) {
        event.preventDefault();

        if (!this.isFormValid()) {
            return;
        }

        this.props.saveProduct();
    }

    deleteProduct(event: any) {
        event.preventDefault();

        if (confirm(gettext('Would you like to delete product: {{name}}', {name: this.props.productToEdit.name}))) {
            this.props.deleteProduct();
        }
    }

    render() {
        const progressStyle: any = {width: '25%'};
        const sectionFilter = (product: any) => !this.props.activeSection || get(product, 'product_type', 'wire') === this.props.activeSection;
        const getActiveSection = () => this.props.sections.filter(s => s._id === this.props.activeSection);

        return (
            <div className="flex-row">
                {(this.props.isLoading ?
                    <div className="col d">
                        <div className="progress">
                            <div className="progress-bar" style={progressStyle} />
                        </div>
                    </div>
                    :
                    <div className="flex-col flex-column">
                        {this.props.activeQuery && (
                            <SearchResults
                                totalItems={this.props.totalProducts}
                                totalItemsLabel={this.props.activeQuery}
                            />
                        )}
                        <ProductList
                            products={this.props.products.filter(sectionFilter)}
                            onClick={this.props.selectProduct}
                            activeSection={this.props.activeSection}
                            activeProductId={this.props.activeProductId} />
                    </div>
                )}
                {this.props.productToEdit &&
                    <EditProduct
                        product={this.props.productToEdit}
                        onChange={this.props.editProduct}
                        errors={this.props.errors}
                        onSave={this.save}
                        onClose={this.props.cancelEdit}
                        onDelete={this.deleteProduct}
                        fetchCompanies={this.props.fetchCompanies}
                        fetchNavigations={this.props.fetchNavigations}
                        companies={this.props.companies}
                        navigations={this.props.navigations}
                        saveCompanies={this.props.saveCompanies}
                        saveNavigations={this.props.saveNavigations}
                        sections={getActiveSection()}
                    />
                }
            </div>
        );
    }
}

Products.propTypes = {
    activeSection: PropTypes.string.isRequired,

    products: PropTypes.arrayOf(PropTypes.object),
    productToEdit: PropTypes.object,
    activeProductId: PropTypes.string,
    selectProduct: PropTypes.func,
    editProduct: PropTypes.func,
    saveProduct: PropTypes.func,
    deleteProduct: PropTypes.func,
    newProduct: PropTypes.func,
    cancelEdit: PropTypes.func,
    isLoading: PropTypes.bool,
    activeQuery: PropTypes.string,
    totalProducts: PropTypes.number,
    fetchCompanies: PropTypes.func,
    fetchNavigations: PropTypes.func,
    errors: PropTypes.object,
    dispatch: PropTypes.func,
    companies: PropTypes.arrayOf(PropTypes.object),
    navigations: PropTypes.arrayOf(PropTypes.object),
    sections: sectionsPropType,
    saveCompanies: PropTypes.func.isRequired,
    saveNavigations: PropTypes.func.isRequired,
};

const mapStateToProps = (state: any) => ({
    products: state.products.map((id) => state.productsById[id]),
    productToEdit: state.productToEdit,
    activeProductId: state.activeProductId,
    isLoading: state.isLoading,
    activeQuery: searchQuerySelector(state),
    totalProducts: state.totalProducts,
    companies: state.companies,
    companiesById: state.companiesById,
    navigations: state.navigations,
    errors: state.errors,
    sections: sectionsSelector(state),
});

const mapDispatchToProps = (dispatch: any) => ({
    selectProduct: (_id: any) => dispatch(selectProduct(_id)),
    editProduct: (event: any) => dispatch(editProduct(event)),
    saveProduct: (type: any) => dispatch(postProduct(type)),
    deleteProduct: (type: any) => dispatch(deleteProduct(type)),
    newProduct: () => dispatch(newProduct()),
    saveCompanies: (companies: any) => dispatch(saveCompanies(companies)),
    fetchCompanies: () => dispatch(fetchCompanies()),
    saveNavigations: (navigations: any) => dispatch(saveNavigations(navigations)),
    fetchNavigations: () => dispatch(fetchNavigations()),
    cancelEdit: (event: any) => dispatch(cancelEdit(event)),
    dispatch: dispatch,
});

export default connect(mapStateToProps, mapDispatchToProps)(Products);
