import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {connect} from 'react-redux';
import {get} from 'lodash';

import {getEditUsers} from 'actions';
import {gettext, fullDate, getItemFromArray} from 'utils';

class AuditInformation extends React.Component<any, any> {
    componentWillMount() {
        if (!get(this.props, 'users.length')) {
            this.props.getEditUsers(this.props.item);
        }
    }

    componentWillReceiveProps(nextProps: any) {
        if (!get(this.props, 'users.length') && (
            get(this.props, 'item._created') !== get(nextProps, 'item._created') ||
            get(this.props, 'item._updated') !== get(nextProps, 'item._updated')
        )) {
            nextProps.getEditUsers(nextProps.item);
        }
    }

    getElement(field: any) {
        const {item} = this.props;
        const users = get(this.props, 'users.length') ? this.props.users : this.props.editUsers;
        const system = gettext('System');

        if (field === '_created' && item._created) {
            const creator = getItemFromArray(item.original_creator,
                users || []);
            return (
                <div className='wire-column__preview__date'>
                    {gettext('Created by {{author}} at {{date}}',
                        {
                            author: creator ? creator.first_name + ' ' + creator.last_name : system,
                            date: fullDate(item._created),
                        }
                    )}
                </div>
            );
        }

        if (field === '_updated' && item.version_creator) {
            const updater = getItemFromArray(item.version_creator, (users || []));
            return (
                <div className='wire-column__preview__date'>
                    {gettext('Updated by {{author}} at {{date}}',
                        {
                            author: updater ? updater.first_name + ' ' + updater.last_name : system,
                            date: fullDate(item._updated),
                        }
                    )}
                </div>
            );
        }

        return null;
    }

    render () {
        const {noPadding} = this.props;
        return (
            <div className={classNames(
                'wire-column__preview__top-bar pt-0 audit-information',
                {
                    'pt-2': !noPadding,
                    'ps-0': noPadding,
                    [this.props.className]: this.props.className != null,
                }
            )}>
                {this.getElement('_created')}
                {this.getElement('_updated')}
            </div>
        );
    }
}

AuditInformation.propTypes = {
    item: PropTypes.object,
    editUsers: PropTypes.array,
    getEditUsers: PropTypes.func.isRequired,
    noPadding: PropTypes.bool,
    users: PropTypes.array,
    className: PropTypes.string,
};

const mapStateToProps = (state: any) => ({editUsers: state.editUsers});

const mapDispatchToProps = (dispatch: any) => ({
    getEditUsers: (item: any) => dispatch(getEditUsers(item))
});

const component: React.ComponentType<any> = connect(mapStateToProps, mapDispatchToProps)(AuditInformation);

export default component;
