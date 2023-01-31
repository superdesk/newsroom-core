import * as React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';

import {gettext} from 'utils';
import DropdownFilter from 'components/DropdownFilter';

export class UserListCompanyFilter extends React.PureComponent {
    constructor(props) {
        super(props);

        this.filter = {
            label: gettext('All Companies'),
            field: 'company',
        };

        this.onChange = this.onChange.bind(this);
        this.getDropdownItems = this.getDropdownItems.bind(this);
    }

    onChange(field, value) {
        this.props.setCompany(value);
        this.props.fetchUsers();
    }

    getDropdownItems(filter) {
        return this.props.companies.map((item, i) => (<button
            key={i}
            className='dropdown-item'
            onClick={() => {this.onChange(filter.field, item._id);}}
            disabled={item._id === this.props.company}
        >{item.name}</button>));
    }

    getActiveQuery() {
        return {
            company: this.props.company ? [get(this.props.companies.find((c) => c._id === this.props.company), 'name')] :
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
                buttonProps={{
                    textOnly: true,
                    iconColour: 'gray-dark'
                }}
            />
        )
    }
}

UserListCompanyFilter.propTypes = {
    companies: PropTypes.arrayOf(PropTypes.object),
    company: PropTypes.string,

    setCompany: PropTypes.func,
    fetchUsers: PropTypes.func,
}
