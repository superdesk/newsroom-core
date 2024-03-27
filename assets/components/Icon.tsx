import * as React from 'react';
import classNames from 'classnames';

interface IProps {
    name: string;
    size?: 'small' | 'medium'; // defaults to 'medium'
    className?: string;
    ariaHidden?: boolean;
}

export class Icon extends React.PureComponent<IProps> {
    render() {
        const classes = classNames(this.props.className, {
            [`icon--${this.props.name}`]: this.props.name,
        });

        return (
            <i
                className={classes}
                aria-label={this.props.name}
                aria-hidden={this.props.ariaHidden}
            />
        );
    }
}
