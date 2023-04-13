import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import ListBar from 'assets/components/ListBar';
import SectionSwitch from 'assets/features/sections/SectionSwitch';
import {sectionsSelector, activeSectionSelector} from 'assets/features/sections/selectors';
import {sectionsPropType} from 'assets/features/sections/types';
import {setSearchQuery} from 'assets/search/actions';
import {gettext} from 'assets/utils';
import {fetchProducts, newProduct} from '../actions';
import Products from './Products';

class ProductsApp extends React.Component<any, any> {
    static propTypes: any;
    constructor(props: any, context: any) {
        super(props, context);
    }

    render() {
        return [
            <ListBar key="bar"
                onNewItem={this.props.newProduct}
                setQuery={this.props.setQuery}
                fetch={this.props.fetchProducts}
                buttonText={gettext('New Product')}
            >
                <SectionSwitch
                    sections={this.props.sections}
                    activeSection={this.props.activeSection}
                />
            </ListBar>,
            <Products key="products" activeSection={this.props.activeSection} sections={this.props.sections} />
        ];
    }
}

ProductsApp.propTypes = {
    sections: sectionsPropType,
    activeSection: PropTypes.string.isRequired,

    fetchProducts: PropTypes.func,
    setQuery: PropTypes.func,
    newProduct: PropTypes.func,
};

const mapStateToProps = (state: any) => ({
    sections: sectionsSelector(state),
    activeSection: activeSectionSelector(state),
});

const mapDispatchToProps = {
    fetchProducts,
    setQuery: setSearchQuery,
    newProduct,
};

export default connect(mapStateToProps, mapDispatchToProps)(ProductsApp);
