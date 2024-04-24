import * as React from 'react';
import classNames from 'classnames';

interface IProps {
    orientation?: 'horizontal' | 'vertical'; // defaults to 'horizontal'
    justify?: 'start' | 'end' | 'center'; // defaults to 'start'
    align?: 'start' | 'end' | 'center'; // defaults to 'center'
    children: React.ReactNode;
}
export class LabelGroup extends React.PureComponent<IProps> {
    render() {
        const classes = classNames('label-group', {
            ['label-group--align-center']: this.props.align === undefined && this.props.orientation !== 'vertical',
            [`label-group--justify-${this.props.justify}`]: this.props.justify,
            [`label-group--align-${this.props.align}`]: this.props.align,
            ['label-group--vertical']: this.props.orientation === 'vertical',
        });

        return (
            <div className={classes} role='group'>
                {this.props.children}
            </div>
        );
    }
}
