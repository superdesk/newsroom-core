import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {gettext} from 'utils';

export class CollapseBoxWithButton extends React.Component {
    constructor(props) {
        super(props);

        this.state = {open: this.props.initiallyOpen};
    }

    render() {
        const contentId = this.props.id + '-content';

        return (
            <div id={this.props.id} 
                className={classNames('nh-collapsible-panel pt-0 nh-collapsible-panel--small', {
                    'nh-collapsible-panel--open': this.state.open,
                    'nh-collapsible-panel--closed': !this.state.open,
                })}>
                <div className="nh-collapsible-panel__header">
                    <div className='nh-collapsible-panel__button'
                        role='button'
                        aria-expanded={this.state.open}
                        aria-controls={contentId}
                        onClick={() => {
                            this.setState({open: !this.state.open});
                        }}>
                        <div className="nh-collapsible-panel__caret">
                            <i className="icon--arrow-right"></i>
                        </div>
                        <h3 className='nh-collapsible-panel__title'>{this.props.buttonText}</h3>
                    </div>
                    <div className='nh-collapsible-panel__line'></div>
                    {this.props.edit && (
                        <button className='nh-button nh-button--tertiary nh-button--small' onClick={this.props.edit}>{gettext('Edit')}</button>
                    )}
                </div>
                <div id={contentId} className='nh-collapsible-panel__content-wraper'>
                    <div className='nh-collapsible-panel__content'>
                        {this.props.children}
                    </div>
                </div>
            </div>
        );
    }
}

CollapseBoxWithButton.propTypes = {
    id: PropTypes.string.isRequired,
    buttonText: PropTypes.string.isRequired,
    initiallyOpen: PropTypes.bool,
    children: PropTypes.node.isRequired,
    edit: PropTypes.func,
};
