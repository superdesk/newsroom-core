import React from 'react';
import 'react-toggle/style.css';
import {Tooltip} from 'bootstrap';

import {gettext, isTouchDevice} from 'utils';

interface IProps {
    newItems?: Array<string>; // array of IDs
    refresh(): void;
}

class NewItemsIcon extends React.Component<IProps> {
    private dom: any;
    private tooltip: any;

    constructor(props: any) {
        super(props);

        this.dom = {tooltip: null};
        this.tooltip = null;
    }

    componentDidMount() {
        if (!isTouchDevice() && this.dom.tooltip) {
            this.tooltip = new Tooltip(this.dom.tooltip);
        }
    }

    componentWillUnmount() {
        if (this.dom.tooltip && this.tooltip) {
            this.tooltip.dispose();
        }
    }

    componentWillUpdate() {
        this.componentWillUnmount();
    }

    componentDidUpdate() {
        this.componentDidMount();
    }

    render() {
        const newItems = this.props.newItems ?? [];

        /**
         * one added item and one removed item would result in action count of 2
         */
        const additionOrRemovalActionCount = newItems.length > 25 ?
            '25+' :
            newItems.length;

        return (
            <button
                type="button"
                ref={(elem: any) => this.dom.tooltip = elem}
                title={gettext('refresh')}
                aria-label={gettext('refresh')}
                className="button__reset-styles d-flex align-items-center ms-3"
                onClick={this.props.refresh}
            >
                <i className="icon--refresh icon--pink" />
                <span className="badge rounded-pill bg-info ms-2">
                    {additionOrRemovalActionCount}
                </span>
            </button>
        );
    }
}

export default NewItemsIcon;
