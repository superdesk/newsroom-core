import * as React from 'react';
import classNames from 'classnames';

interface IProps {
    id: string;
    title: string | ((open: boolean) => string);
    initiallyOpen?: boolean;
    drawHeaderLine?: boolean;
    headerButtons?: React.ReactNode;
    className?: string | ((open: boolean) => string);
    children: React.ReactNode;
}

interface IState {
    open: boolean;
}

export class CollapseBox extends React.Component<IProps, IState> {
    constructor(props: IProps) {
        super(props);

        this.state = {open: this.props.initiallyOpen === true};
    }

    render() {
        const contentId = this.props.id + '-content';
        const className = typeof this.props.className === 'function' ?
            this.props.className(this.state.open) :
            this.props.className || '';

        return (
            <div id={this.props.id}
                className={classNames('nh-collapsible-panel pt-0 nh-collapsible-panel--small', {
                    'nh-collapsible-panel--open': this.state.open,
                    'nh-collapsible-panel--closed': !this.state.open,
                    [className ?? '']: className?.length > 0,
                })}>
                <div className="nh-collapsible-panel__header">
                    <div className="nh-collapsible-panel__button"
                        role="button"
                        aria-expanded={this.state.open}
                        aria-controls={contentId}
                        onClick={() => {
                            this.setState({open: !this.state.open});
                        }}>
                        <div className="nh-collapsible-panel__caret">
                            <i className="icon--arrow-right" />
                        </div>
                        <h3 className="nh-collapsible-panel__title">
                            {typeof this.props.title === 'function' ?
                                this.props.title(this.state.open) :
                                this.props.title
                            }
                        </h3>
                    </div>
                    {this.props.drawHeaderLine !== true ? null : (
                        <div className="nh-collapsible-panel__line"/>
                    )}
                    {this.props.headerButtons}
                </div>
                <div id={contentId} className="nh-collapsible-panel__content-wraper">
                    <div className="nh-collapsible-panel__content">
                        {this.props.children}
                    </div>
                </div>
            </div>
        );
    }
}
