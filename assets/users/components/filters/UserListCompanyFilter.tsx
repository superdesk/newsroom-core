import * as React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';

import {gettext} from 'utils';
import DropdownFilter from 'components/DropdownFilter';

export class UserListCompanyFilter extends React.PureComponent<any, any> {
    static propTypes: any;
    filter: {label: any; field: string;};

    constructor(props: any) {
        super(props);

        this.filter = {
            label: gettext('All Companies'),
            field: 'company',
        };

        this.onChange = this.onChange.bind(this);
        this.getDropdownItems = this.getDropdownItems.bind(this);
    }

    onChange(field: any, value: any) {
        this.props.setCompany(value);
        this.props.fetchUsers();
    }

    getDropdownItems(filter: any) {
        return this.props.companies.map((item: any, i: number) => (<button
            key={i}
            className='dropdown-item'
            onClick={() => {this.onChange(filter.field, item._id);}}
            disabled={item._id === this.props.company}
        >{item.name}</button>));
    }

    getActiveQuery() {
        return {
            company: this.props.company ? [get(this.props.companies.find((c: any) => c._id === this.props.company), 'name')] :
                null,
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

UserListCompanyFilter.propTypes = {
    companies: PropTypes.arrayOf(PropTypes.object),
    company: PropTypes.string,

    setCompany: PropTypes.func,
    fetchUsers: PropTypes.func,
};
