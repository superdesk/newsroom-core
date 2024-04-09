import * as React from 'react';
import {connect} from 'react-redux';
import {get} from 'lodash';

import {gettext} from 'utils';
import {currentCompanySelector, companySectionListSelector} from '../selectors';

import DropdownFilter from 'components/DropdownFilter';

interface IReduxProps {
    currentCompany: {
        _id: string;
        products: Array<{_id: string}>;
    };
    companySections: any;
}

interface IOwnProps {
    products: Array<any>;
    product?: string;
    setProductFilter: (value: any) => void;
}

type IProps = IOwnProps & IReduxProps;

class CompanyDetailsProductFilterComponent extends React.PureComponent<IProps> {
    filter: {
        label: string;
        field: string;
    };

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
        const sectionIds = new Set(this.props.companySections[this.props.currentCompany._id].map((section: any) => section._id));
        const currentCompanyProducts: Set<string> = new Set(this.props.currentCompany.products.map(({_id}) => _id));

        return this.props.products
            .filter((product: any) => sectionIds.has(product.product_type) && currentCompanyProducts.has(product._id))
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
            />
        );
    }
}

const mapStateToProps = (state: any) => ({
    currentCompany: currentCompanySelector(state),
    companySections: companySectionListSelector(state),
});

export const CompanyDetailsProductFilter: React.ComponentType<IOwnProps>
    = connect<IReduxProps, {}, IOwnProps>(mapStateToProps)(CompanyDetailsProductFilterComponent);
