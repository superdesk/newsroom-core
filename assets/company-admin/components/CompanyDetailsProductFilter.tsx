import * as React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';

import {gettext} from 'utils';
import {currentCompanySelector, companySectionListSelector} from '../selectors';

import DropdownFilter from 'components/DropdownFilter';

class CompanyDetailsProductFilterComponent extends React.PureComponent<any, any> {
    static propTypes: any;
    filter: any;
    constructor(props: any) {
        super(props);

        this.filter = {
            label: gettext('All Products'),
            field: 'product',
        };

        this.onChange = this.onChange.bind(this);
        this.getDropdownItems = this.getDropdownItems.bind(this);
    }

    onChange(field: any, value: any) {
        this.props.setProductFilter(value);
    }

    getDropdownItems(filter: any) {
        const sectionIds = this.props.companySections[this.props.currentCompany._id].map((section: any) => section._id);

        return this.props.products
            .filter((product: any) => sectionIds.includes(product.product_type))
            .map((product: any) => (
                <button
                    key={product._id}
                    className="dropdown-item"
                    onClick={() => this.onChange(filter.field, product._id)}
                    disabled={product._id === this.props.product}
                >
                    {product.name}
                </button>
            ));
    }

    getActiveQuery() {
        return {
            product: !this.props.product ? null : [
                get(this.props.products.find((product: any) => product._id === this.props.product), 'name')
            ]
        };
    }

    render() {
        return (
            <DropdownFilter
                key={this.filter.field}
                filter={this.filter}
                getDropdownItems={this.getDropdownItems}
                activeFilter={this.getActiveQuery()}
                toggleFilter={this.onChange}
                buttonProps={{
                    textOnly: true,
                }}
            />
        );
    }
}

CompanyDetailsProductFilterComponent.propTypes = {
    products: PropTypes.arrayOf(PropTypes.object),
    product: PropTypes.string,
    setProductFilter: PropTypes.func,
    currentCompany: PropTypes.object,
    companySections: PropTypes.object,
};

const mapStateToProps = (state: any) => ({
    currentCompany: currentCompanySelector(state),
    companySections: companySectionListSelector(state),
});

export const CompanyDetailsProductFilter: React.ComponentType<any> = connect(mapStateToProps)(CompanyDetailsProductFilterComponent);
