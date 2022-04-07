import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {Collapse} from 'bootstrap';

export class CollapseBoxWithButton extends React.Component {
    constructor(props) {
        super(props);

        this.state = {open: this.props.initiallyOpen};
        this.dom = {content: null};
        this.collapse = null;
    }

    componentDidMount() {
        if (this.dom.content) {
            this.collapse = new Collapse(this.dom.content, {toggle: this.props.initiallyOpen});
            this.dom.content.addEventListener('show.bs.collapse', () => {
                this.setState({open: true});
            });
            this.dom.content.addEventListener('hide.bs.collapse', () => {
                this.setState({open: false});
            });
        }
    }

    componentWillUnmount() {
        if (this.dom.content && this.collapse) {
            this.collapse.dispose();
        }
    }

    render() {
        const contentId = this.props.id + '-content';

        return (
            <div
                id={this.props.id}
                className="d-flex flex-column collapse__container"
            >
                <button
                    className="btn d-flex align-items-center btn-outline-light mb-0"
                    type="button"
                    data-toggle="collapse"
                    data-target={`#${contentId}`}
                    onClick={() => {
                        if (this.state.open) {
                            this.dom.content.classList.toggle('show');
                        }
                    }}
                    aria-expanded={this.state.open}
                    aria-controls={contentId}
                >
                    <span>{this.props.buttonText}</span>
                    <i className={classNames(
                        'icon-small--arrow-down icon--gray-dark ml-auto',
                        {'icon--rotate-180': this.state.open}
                    )} />
                </button>
                <div
                    className="collapse"
                    id={contentId}
                    ref={(elem) => this.dom.content = elem}
                >
                    {this.props.children}
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
};
