import React from 'react';
import {connect} from 'react-redux';

import {IArticle, IListConfig} from 'interfaces';
import {gettext} from 'utils';
import {getVersionsLabelText} from 'wire/utils';
import {fetchVersions, openItem} from '../actions';

import ItemVersion from './ItemVersion';

interface IOwnProps {
    item: IArticle;
    isPreview: boolean;
    inputId?: string;
    displayConfig?: IListConfig;
    matchedIds?: Array<IArticle['_id']>
}

interface IState {
    versions: Array<IArticle>;
    loading: boolean;
    error: boolean;
}

interface IDispatchProps {
    openItem(item: IArticle): void;
}

type IProps = IDispatchProps & IOwnProps;

const mapDispatchToProps = (dispatch: any) => ({
    openItem: (item: IArticle) => dispatch(openItem(item)),
});


class ListItemPreviousVersions extends React.Component<IProps, IState> {
    baseClass: string;
    static defaultProps = {matchedIds: []};

    constructor(props: IProps) {
        super(props);
        this.state = {versions: [], loading: true, error: false};
        this.baseClass = this.props.isPreview ? 'wire-column__preview' : 'wire-articles';
        this.open = this.open.bind(this);
        this.fetch();
    }

    componentDidUpdate(prevProps: Readonly<IProps>) {
        if (prevProps.item._id !== this.props.item._id) {
            this.fetch();
        }
    }

    open(version: IArticle, event: React.MouseEvent) {
        event.stopPropagation();
        this.props.openItem(version);
    }

    fetch() {
        fetchVersions(this.props.item)
            .then((versions) => this.setState({versions, loading: false}))
            .catch(() => this.setState({error: true}));
    }

    render() {
        if (this.state.loading) {
            return (
                <div className={`${this.baseClass}__versions`}>
                    {gettext('Loading')}
                </div>
            );
        }

        const versionLabelText = getVersionsLabelText(this.props.item, this.state.versions.length > 1);
        const versions = this.state.versions.map((version: any) => (
            <ItemVersion
                key={version._id}
                version={version}
                baseClass={this.baseClass}
                withDivider={this.props.isPreview}
                onClick={this.open}
                displayConfig={this.props.displayConfig}
                matchedIds={this.props.matchedIds}
            />
        ));

        return (
            this.props.item.ancestors ?
                <div className={this.baseClass + '__versions'} id={this.props.inputId}>
                    {this.props.isPreview && (
                        <span className="wire-column__preview__versions__box-headline">
                            {gettext('Previous {{ versionsLabel }}', {versionsLabel: versionLabelText})}
                        </span>
                    )}
                    {versions}
                </div> : null
        );
    }
}

const component = connect(null, mapDispatchToProps)(ListItemPreviousVersions);

export default component;
