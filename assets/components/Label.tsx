import * as React from 'react';
import classNames from 'classnames';

interface IProps {
    text: string;
    type?: 'default' | 'success' | 'warning' | 'alert' | 'info' | 'highlight';
    size?: 'small' | 'medium' | 'big';
    style?: 'fill' | 'hollow' | 'translucent'; // defaults to 'fill'
    className?: string;
}

export class Label extends React.PureComponent<IProps> {
    render() {
        const classes = classNames('label label--rounded', {
            'label--default': !this.props.type,
            [`label--${this.props.type}`]: this.props.type !== undefined,
            [`label--${this.props.style}`]: this.props.style,
            [`label--${this.props.size}`]: this.props.size,
        }, this.props.className);

        return (
            <span className={classes}>
                {this.props.text}
            </span>
        );
    }
}
