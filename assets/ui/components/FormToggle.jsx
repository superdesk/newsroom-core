import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

export class FormToggle extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            expanded: !!this.props.expanded,
        };

        this.toggle = this.toggle.bind(this);
    }

    toggle() {
        this.setState({expanded: !this.state.expanded});
    }

    render() {
        return (
            <React.Fragment>
                <div
                    className="list-item__preview-collapsible"
                    onClick={this.toggle}
                >
                    <div className="list-item__preview-collapsible-header">
                        <i className={classNames(
                            'icon--arrow-right icon--gray-dark',
                            {'icon--rotate-90': this.state.expanded}
                        )} />
                        <h3>{this.props.title}</h3>
                    </div>
                </div>
                {!this.state.expanded ? null : (
                    this.props.children
                )}
            </React.Fragment>
        )
    }
}

FormToggle.propTypes = {
    expanded: PropTypes.bool,
    title: PropTypes.string.isRequired,
    children: PropTypes.oneOfType([
        PropTypes.arrayOf(PropTypes.node),
        PropTypes.node,
    ]).isRequired,
}
