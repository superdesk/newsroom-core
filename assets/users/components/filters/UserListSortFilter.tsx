import * as React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import classNames from 'classnames';

import {gettext} from 'utils';

import DropdownFilter from 'components/DropdownFilter';

export class UserListSortFilter extends React.PureComponent<any, any> {
    static propTypes: any;
    filter: any;
    sortFields: any;
    constructor(props: any) {
        super(props);

        this.filter = {
            field: 'sort',
            label: gettext('Sort By'),
        };
        this.sortFields = [{
            _id: 'first_name',
            name: gettext('First Name'),
        }, {
            _id: 'last_name',
            name: gettext('Last Name'),
        }, {
            _id: 'last_active',
            name: gettext('Last Active'),
        }, {
            _id: '_created',
            name: gettext('Date Created'),
        }, {
            _id: 'user_type',
            name: gettext('User Type'),
        }, {
            _id: 'is_validated',
            name: gettext('User Status'),
        }];

        this.onChange = this.onChange.bind(this);
        this.onSortChanged = this.onSortChanged.bind(this);
        this.getDropdownItems = this.getDropdownItems.bind(this);
        this.getFilterLabel = this.getFilterLabel.bind(this);
    }

    onChange(field: any, value: any) {
        this.props.setSort(value);
        this.props.fetchUsers();
    }

    onSortChanged() {
        this.props.toggleSortDirection();
        this.props.fetchUsers();
    }

    getDropdownItems(filter: any) {
        return this.sortFields.map((item: any, i: any) => (
            <button
                key={i}
                className='dropdown-item'
                onClick={() => {this.onChange(filter.field, item._id);}}
                disabled={item._id === this.props.sort || (!this.props.sort && i === 0)}
            >
                {item.name}
            </button>
        ));
    }

    getActiveQuery() {
        return {
            sort: !this.props.sort ? null : [
                get(this.sortFields.find((s: any) => s._id === this.props.sort), 'name')
            ],
        };
    }

    getFilterLabel(filter: any, activeFilter: any, isActive: any) {
        const label = !isActive ? this.sortFields[0].name : activeFilter[filter.field][0];

        return (
            <React.Fragment>
                <span>{gettext('Sort by:')}</span>
                {label}
            </React.Fragment>
        );
    }

    render() {
        return (
            <React.Fragment>
                <DropdownFilter
                    key={this.filter.field}
                    filter={this.filter}
                    getDropdownItems={this.getDropdownItems}
                    activeFilter={this.getActiveQuery()}
                    toggleFilter={this.onChange}
                    getFilterLabel={this.getFilterLabel}
                    buttonProps={{
                        textOnly: true,
                        iconColour: 'gray-dark'
                    }}
                />
                <div className="btn-group">
                    <button
                        className="icon-button"
                        aria-label={gettext('Sort')}
                        onClick={this.onSortChanged}
                    >
                        <i className={classNames(
                            'icon--filter icon--gray-dark',
                            {'rotate-180': this.props.sortDirection === -1}
                        )} />
                    </button>
                </div>
            </React.Fragment>
        );
    }
}

UserListSortFilter.propTypes = {
    sort: PropTypes.string,
    sortDirection:PropTypes.number,
    setSort: PropTypes.func,
    toggleSortDirection: PropTypes.func,
    fetchUsers: PropTypes.func,
};
