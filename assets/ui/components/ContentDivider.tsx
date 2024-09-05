import React from 'react';
import classNames from 'classnames';

interface IProps {
    type?: 'dashed' |'dotted' | 'solid'; // defaults to 'solid'
    orientation?: 'horizontal' |'vertical'; // defaults to 'horizontal'
    align?: 'center' | 'left' | 'right'; // defaults to 'center'
    margin?: 'x-small' | 'small' |'medium' | 'large' | 'none';
    textSize?: 'small' |'medium' | 'large';
    className?: string;
    children?: React.ReactNode;
}

export class ContentDivider extends React.Component<IProps> {

    render() {
        const classes = classNames('sd-content-divider', {
            'sd-content-divider--horizontal': this.props.orientation === undefined,
            [`sd-content-divider--${this.props.type}`]: this.props.type || this.props.type !== undefined,
            [`sd-content-divider--text-${this.props.align}`]: this.props.align || this.props.align !== undefined,
            [`sd-content-divider--${this.props.orientation}`]:
            this.props.orientation || this.props.orientation !== undefined,
            'sd-content-divider--margin-small': this.props.margin === undefined,
            [`sd-content-divider--margin-${this.props.margin}`]: this.props.margin || this.props.margin !== undefined,

            'sd-content-divider--text-large': this.props.textSize === undefined,
            [`sd-content-divider--text-${this.props.textSize}`]: this.props.textSize || this.props.textSize !== undefined,
        }, this.props.className);

        if (this.props.children) {
            return (
                <div className={'sd-content-divider--with-text ' + classes} role="separator">
                    <span className="sd-content-divider__inner-text">{this.props.children}</span>
                </div>
            );
        }  else {
            return <div className={classes} role="separator"></div>;
        }
    }
}
