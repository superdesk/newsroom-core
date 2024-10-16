import * as React from 'react';
import classNames from 'classnames';

export type IPropsVariant = 'primary' | 'secondary' | 'tertiary';
export type IPropsSize = 'small' | 'medium' | 'large';

export interface IPropsButtonBase {
    value: string;
    variant?: IPropsVariant;
    size?: IPropsSize;
    id?: string;
    className?: string;
    disabled?: boolean;
    'data-test-id'?: string;
}

interface IPropsButton extends IPropsButtonBase {
    type?: 'button',
    onClick(event: React.MouseEvent<HTMLButtonElement, MouseEvent>): void;
}

interface IPropsSubmit extends IPropsButtonBase {
    type?: 'submit',
    onClick?(event: React.MouseEvent<HTMLButtonElement, MouseEvent>): void;
}

interface IPropsReset extends IPropsButtonBase {
    type?: 'reset',
    onClick?(event: React.MouseEvent<HTMLButtonElement, MouseEvent>): void;
}

type IProps = IPropsButton | IPropsSubmit |  IPropsReset;

export class Button extends React.PureComponent<IProps> {
    render() {
        const classes = classNames('nh-button', {
            'nh-button--primary': !this.props.variant,
            [`nh-button--${this.props.size}`]: this.props.size,
            [`nh-button--${this.props.variant}`]: this.props.variant,
            'nh-button--disabled': this.props.disabled,
        }, this.props.className);

        return (
            <button
                type={this.props.type ?? 'button'}
                id={this.props.id}
                className={classes}
                aria-label={this.props.value}
                data-test-id={this.props['data-test-id']}
                tabIndex={0}
                disabled={this.props.disabled}
                onClick={(event) => this.props.onClick && this.props.onClick(event)}
            >
                {this.props.value}
            </button>
        );
    }
}
