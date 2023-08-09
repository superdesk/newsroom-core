import React from 'react';
import PropTypes from 'prop-types';
import {SortableContainer, SortableElement, arrayMove} from 'react-sortable-hoc';
import {gettext} from 'utils';


class SortItems extends React.Component<any, any> {
    static propTypes: any;
    cursor: any;
    constructor(props: any) {
        super(props);
        this.state = {items: this.props.items};
        this.onSortEnd = this.onSortEnd.bind(this);
        this.onSortStart = this.onSortStart.bind(this);
        this.onRemove = this.onRemove.bind(this);
    }

    componentWillReceiveProps(nextProps: any) {
        this.setState({items: nextProps.items});
    }

    onRemove(itemToRemove: any) {
        const items = [...this.state.items].filter((item: any) => itemToRemove.value !== item.value);
        this.setState({items: items});
        this.props.onChange(items);
    }

    onSortEnd({oldIndex, newIndex}: any) {
        const items = arrayMove(this.state.items, oldIndex, newIndex);
        this.setState({items});
        document.body.style.cursor = this.cursor;
        this.props.onChange(items);
    }

    // set cursor to move during whole drag
    onSortStart() {
        this.cursor = document.body.style.cursor;
        document.body.style.cursor = 'move';
    }


    render() {
        const SortableItem = SortableElement(({item}: any) =>
            <li className="list-group-item">
                <span>{item.text}</span>
                <button type="button"
                    className="icon-button icon-button--small float-end"
                    aria-label={gettext('Close')}
                    onClick={(e: any) => {
                        e.preventDefault();
                        e.stopPropagation();
                        this.onRemove(item);
                    }}><i className="icon--close-thin icon--gray-dark"></i>
                </button>
            </li>
        );

        const SortableList = SortableContainer(({items}: any) => {
            return (
                <ul className="list-group flex-grow-1">
                    {items.map((item: any, index: any) => (
                        <SortableItem key={`item-${index}`} index={index} item={item}/>
                    ))}
                </ul>
            );
        });

        return <SortableList
            distance={5}
            items={this.state.items}
            onSortEnd={this.onSortEnd}
            onSortStart={this.onSortStart}
        />;
    }
}

SortItems.propTypes = {
    items: PropTypes.array.isRequired,
    onChange: PropTypes.func.isRequired,
};

export default SortItems;