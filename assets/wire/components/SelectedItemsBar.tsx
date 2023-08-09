import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {isEmpty} from 'lodash';

import {gettext} from 'utils';

import {selectAll, selectNone} from 'wire/actions';

class SelectedItemsBar extends React.PureComponent<any, any> {
    static propTypes: any;
    constructor(props: any) {
        super(props);
        this.onAction = this.onAction.bind(this);
    }

    onAction(event: any, action: any) {
        event.preventDefault();
        action.action(this.props.selectedItems) && this.props.selectNone();
    }

    render() {
        if (isEmpty(this.props.selectedItems)) {
            return null;
        }

        const multiActionFilter = (action: any) => action.multi &&
            this.props.selectedItems.every((item: any) => !action.when || action.when(this.props.state, this.props.itemsById[item]));

        const actions = this.props.actions.filter(multiActionFilter).map((action: any) => (
            <button className='icon-button icon-button--primary'
                key={action.name}
                title={action.name}
                onClick={(e: any) => this.onAction(e, action)}
                aria-label={gettext(action.name)}
            >
                <i className={`icon--${action.icon}`}></i>
            </button>
        ));

        return (
            <div className='multi-action-bar multi-action-bar--open'>
                <button className='nh-button nh-button--primary me-2'
                    onClick={this.props.selectAll}>{gettext('Select All')}
                </button>

                <button className='nh-button nh-button--secondary'
                    onClick={this.props.selectNone}>{gettext('Cancel')}
                </button>

                <span className='multi-action-bar__count'>
                    {gettext('{{ count }} item(s) selected', {count: this.props.selectedItems.length})}
                </span>
                <div className='multi-action-bar__icons'>
                    {actions}
                </div>
            </div>
        );
    }
}

SelectedItemsBar.propTypes = {
    state: PropTypes.object.isRequired,
    itemsById: PropTypes.object.isRequired,
    selectedItems: PropTypes.array.isRequired,
    actions: PropTypes.array.isRequired,

    selectAll: PropTypes.func.isRequired,
    selectNone: PropTypes.func.isRequired,
};

const mapStateToProps = (state: any) => ({
    state: state,
    itemsById: state.itemsById,
    selectedItems: state.selectedItems,
});

const mapDispatchToProps: any = {
    selectAll,
    selectNone,
};

const component: React.ComponentType<any> = connect(mapStateToProps, mapDispatchToProps)(SelectedItemsBar);

export default component;
