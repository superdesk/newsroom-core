import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

export class CollapseBoxWithButton extends React.Component {
    constructor(props) {
        super(props);

        this.state = {open: this.props.initiallyOpen};
        this.dom = {content: null};
    }

    componentDidMount() {
        $(this.dom.content).collapse({toggle: this.props.initiallyOpen});

        $(this.dom.content).on('show.bs.collapse', () => {
            this.setState({open: true});
        });
        $(this.dom.content).on('hide.bs.collapse', () => {
            this.setState({open: false});
        });
    }

    componentWillUnmount() {
        $(this.dom.content).collapse('dispose');
    }

    render() {
        const contentId = this.props.id + '-content';

        return (
            <div
                id={this.props.id}
                className="d-flex flex-column collapse__container"
            >
                <button
                    className="btn d-flex align-items-center btn-outline-secondary mb-0"
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
