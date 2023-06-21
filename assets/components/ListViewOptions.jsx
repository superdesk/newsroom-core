import React from 'react';
import PropTypes from 'prop-types';
import {Tooltip} from 'bootstrap';

import {gettext} from 'utils';

import {EXTENDED_VIEW, COMPACT_VIEW} from 'wire/defaults';
import {isTouchDevice} from 'utils';

class ListViewOptions extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {isOpen: false};
        this.views = [
            {type: EXTENDED_VIEW, label: gettext('Large list')},
            {type: COMPACT_VIEW, label: gettext('Compact list')},
            //{type: 'grid', label: gettext('Grid')},
        ];

        this.toggleOpen = this.toggleOpen.bind(this);
        this.handleClickOutside = this.handleClickOutside.bind(this);
        this.tooltip = null;
    }

    toggleOpen() {
        this.setState({isOpen: !this.state.isOpen});
    }

    setView(view) {
        this.setState({isOpen: false});
        this.props.setView(view.type);
    }

    componentDidMount() {
        if ( !isTouchDevice() ) {
            if (this.elem) {
                this.tooltip = new Tooltip(this.elem);
            }
            document.addEventListener('mousedown', this.handleClickOutside);
        }
    }

    componentWillUnmount() {
        if (this.elem && this.tooltip) {
            this.tooltip.dispose();
        }
        document.removeEventListener('mousedown', this.handleClickOutside);
    }

    handleClickOutside(e) {
        if (this.state.isOpen && !this.elem.contains(e.target)) {
            this.setState({isOpen: false});
        }
    }

    render() {
        return (
            <React.Fragment>
                <a
                    className="icon-link--plain"
                    ref={(elem) => this.elem = elem}
                    onClick={this.toggleOpen}
                >
                    <span className="icon-link__text">{gettext('Change view')}</span>
                    <i className={`icon--${this.props.activeView}`} />
                </a>
                {this.state.isOpen && (
                    <div className='dropdown-menu dropdown-menu-right show'>
                        <h6 className='dropdown-header'>{gettext('Change view')}</h6>
                        {this.views.map((view) => (
                            <button
                                key={view.type}
                                className='dropdown-item'
                                onClick={() => this.setView(view)}
                                aria-label={view.label}
                                type='button'
                            >
                                <i className={`icon--${view.type}`} />
                                {' '}{view.label}
                            </button>
                        ))}
                    </div>
                )}
            </React.Fragment>
        );
    }
}

ListViewOptions.propTypes = {
    activeView: PropTypes.string,
    setView: PropTypes.func.isRequired,
};

export default ListViewOptions;
