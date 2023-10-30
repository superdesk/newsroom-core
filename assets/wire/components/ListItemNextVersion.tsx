import React from 'react';
import {connect} from 'react-redux';

import {IArticle} from 'interfaces';
import {newshubApi} from 'api';
import {gettext} from 'utils';
import ItemVersion from './ItemVersion';
import {fetchNext, openItem} from '../actions';

interface IOwnProps {
    item: IArticle;
    displayConfig: {[field: string]: boolean};
}

interface IState {
    next: IArticle | null;
}

interface IDispatchProps {
    openItem(item: IArticle): void;
}

type IProps = IDispatchProps & IOwnProps;

const mapDispatchToProps = (dispatch: any) => ({
    openItem: (item: IArticle) => dispatch(openItem(item)),
});

class ListItemNextVersion extends React.Component<IProps, IState> {
    constructor(props: IProps) {
        super(props);
        this.state = {next: null};
        this.open = this.open.bind(this);
        this.fetch();
    }

    componentDidUpdate(prevProps: Readonly<IProps>) {
        if (prevProps.item.nextversion !== this.props.item.nextversion) {
            this.fetch();
        }
    }

    fetch() {
        fetchNext(this.props.item)
            .then((next) => this.setState({next: next}))
            .catch(() => this.setState({next: null}));
    }

    open(version: any, event: any) {
        if (this.state.next == null) {
            return;
        }

        event.stopPropagation();
        this.props.openItem(this.state.next);
    }

    render() {
        if (!this.state.next) {
            return null;
        }

        const versionLabelText = newshubApi.ui.wire.getVersionsLabelText(this.props.item, false);
        const baseClass = 'wire-column__preview';

        return (
            <div className={`${baseClass}__versions`}>
                <span className={`${baseClass}__versions__box-headline`}>
                    {gettext('Next {{ versionsLabel }}', {versionsLabel: versionLabelText})}
                </span>

                <ItemVersion
                    version={this.state.next}
                    baseClass={baseClass}
                    onClick={this.open}
                    displayConfig={this.props.displayConfig}
                />
            </div>
        );
    }
}

const component= connect(null, mapDispatchToProps)(ListItemNextVersion);

export default component;
