import React from 'react';
import classNames from 'classnames';

interface IProps {
    isOpenDefault: boolean;
    id?: string;
    children?: React.ReactNode;
    labelCollapsed: string;
    labelOpened: string;
}

interface IState {
    open: boolean;
}

export default class BannerDrop extends React.Component<IProps, IState> {
    constructor(props: IProps) {
        super(props);
        this.state = {
            open: this.props.isOpenDefault
        };
        this.toggleOpen = this.toggleOpen.bind(this);
    }

    componentWillReceiveProps(nextProps: IProps) {
        if (this.props.id !== nextProps.id &&
                this.state.open !== nextProps.isOpenDefault) {
            this.setState({open: nextProps.isOpenDefault});
        }
    }

    toggleOpen() {
        this.setState({open: !this.state.open});
    }

    render() {
        const label = this.state.open ? this.props.labelOpened : this.props.labelCollapsed;
        return (<div className="banner-drop">
            <div className={classNames('banner-drop__child',
                {'banner-drop__child--active': this.state.open})}>
                {this.props.children}
            </div>
            <div className="banner-drop__toggle">
                <div className="banner-drop__line banner-drop__line--left" />
                <button type="button" className={classNames({'active': this.state.open})}>
                    <i className="banner-drop__toggle icon-small--arrow-down" onClick={this.toggleOpen} />
                </button>
                <div className="banner-drop__line banner-drop__line--right" />
            </div>
            <div className={classNames('banner-drop__text',
                {'banner-drop__text--active': this.state.open})}>{label}</div>
        </div>);
    }
}
