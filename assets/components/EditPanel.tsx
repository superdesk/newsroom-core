import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from '../utils';
import {isEmpty, get, pickBy, isEqual, every} from 'lodash';
import CheckboxInput from 'components/CheckboxInput';

class EditPanel extends React.Component<any, any> {
    constructor(props: any) {
        super(props);
        this.onItemChange = this.onItemChange.bind(this);
        this.toggleSelectAll = this.toggleSelectAll.bind(this);
        this.saveItems = this.saveItems.bind(this);
        this.initItems = this.initItems.bind(this);
        this.state = {activeParent: props.parent._id, items: {}};
    }

    onItemChange(event: any) {
        const item = event.target.name;
        const items = Object.assign({}, this.state.items);
        items[item] = !items[item];
        this.updateItems(items);
    }

    toggleSelectAll(availableItems: any, allActive: any) {
        let items: any = {};

        if (!allActive) {
            availableItems.forEach((item: any) => {
                items[item._id] = true;
            });
        }

        this.updateItems(items);
    }

    updateItems(items: any) {
        this.setState({items});
        if (this.props.onChange) {
            this.props.onChange({
                target: {
                    name: this.props.field,
                    value: Object.keys(items).filter((k: any) => items[k])
                }
            });
        }
    }

    saveItems(event: any) {
        event.preventDefault();
        this.props.onSave(Object.keys(pickBy(this.state.items)));
    }

    initItems(props: any) {
        const items: any = {};
        props.items.map((item: any) =>
            items[item._id] = (props.parent[props.field] || []).includes(item._id));

        this.setState({activeParent: props.parent._id, items});
    }

    componentWillMount() {
        this.initItems(this.props);
    }

    componentWillReceiveProps(nextProps: any) {
        if (this.state.activeParent !== nextProps.parent._id ||
            get(this.props, 'items.length', 0) !== get(nextProps, 'items.length', 0)) {
            this.initItems(nextProps);
            return;
        }

        let items: any = {};
        nextProps.items.map((item: any) =>
            items[item._id] = (nextProps.parent[nextProps.field] || []).includes(item._id));
        if (!isEqual(this.state.items, items)) {
            this.initItems(nextProps);
        }

    }

    renderList(items: any) {
        const allActive = every(items, (item) => {
            return !!this.state.items[item._id];
        });

        return (
            <ul className="list-unstyled">
                {!this.props.includeSelectAll ? null : (
                    <li style={{borderBottom: '1px dotted #cacaca'}}>
                        <CheckboxInput
                            name="select_all"
                            label={allActive ? gettext('Deselect All') : gettext('Select All')}
                            onChange={() => this.toggleSelectAll(items, allActive)}
                            value={allActive}
                        />
                    </li>
                )}
                {items.map((item: any) => (
                    <li key={item._id}>
                        <CheckboxInput
                            name={item._id}
                            label={item.name}
                            value={!!this.state.items[item._id]}
                            onChange={this.onItemChange} />
                    </li>
                ))}
            </ul>
        );
    }

    render() {
        return (
            <div className='tab-pane active' id='navigations'>
                <form onSubmit={this.saveItems}>
                    <div className="list-item__preview-form">
                        {!this.props.title ? null : (
                            <div>{this.props.title}</div>
                        )}
                        {!isEmpty(this.props.groups) && this.props.groups.map((group: any) => (
                            <div className="form-group" key={group._id}>
                                <label>{group.name}</label>
                                {this.renderList(this.props.items.filter((item: any) => get(item, this.props.groupField, this.props.groupDefaultValue) === group._id))}
                            </div>
                        ))}
                        {isEmpty(this.props.groups) && this.renderList(this.props.items)}
                    </div>
                    <div className='list-item__preview-footer'>
                        {this.props.onCancel && (
                            <input
                                type="button"
                                className="btn btn-outline-secondary"
                                value={gettext('Cancel')}
                                onClick={this.props.onCancel}
                                disabled={this.props.cancelDisabled}
                            />
                        )}
                        <input
                            type='submit'
                            className='btn btn-outline-primary'
                            value={gettext('Save')}
                            disabled={this.props.saveDisabled}
                        />
                    </div>
                </form>
            </div>
        );
    }

}

EditPanel.propTypes = {
    parent: PropTypes.object.isRequired,
    items: PropTypes.arrayOf(PropTypes.object),
    field: PropTypes.string,
    onSave: PropTypes.func.isRequired,
    groups: PropTypes.arrayOf(PropTypes.shape({
        _id: PropTypes.string,
        name: PropTypes.string,
    })),
    groupField: PropTypes.string,
    groupDefaultValue: PropTypes.string,
    onChange: PropTypes.func,
    cancelDisabled: PropTypes.bool,
    saveDisabled: PropTypes.bool,
    onCancel: PropTypes.func,
    includeSelectAll: PropTypes.bool,
    title: PropTypes.string,
};

export default EditPanel;
