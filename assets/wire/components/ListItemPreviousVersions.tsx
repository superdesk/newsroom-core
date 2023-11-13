import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {gettext} from 'utils';
import {getVersionsLabelText} from 'wire/utils';
import {fetchVersions, openItem} from '../actions';

import ItemVersion from './ItemVersion';


class ListItemPreviousVersions extends React.Component<any, any> {
    baseClass: string;
    static propTypes: any;
    static defaultProps: any;

    constructor(props: any) {
        super(props);
        this.state = {versions: [], loading: true, error: false};
        this.baseClass = this.props.isPreview ? 'wire-column__preview' : 'wire-articles';
        this.open = this.open.bind(this);
        this.fetch(props);
    }

    componentWillReceiveProps(nextProps: any) {
        if (nextProps.item._id !== this.props.item._id) {
            this.fetch(nextProps);
        }
    }

    open(version: any, event: any) {
        event.stopPropagation();
        this.props.dispatch(openItem(version));
    }

    fetch(props: any) {
        props.dispatch(fetchVersions(props.item))
            .then((versions: any) => this.setState({versions, loading: false}))
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

ListItemPreviousVersions.propTypes = {
    item: PropTypes.shape({
        _id: PropTypes.string,
        ancestors: PropTypes.array,
    }).isRequired,
    isPreview: PropTypes.bool.isRequired,
    dispatch: PropTypes.func,
    inputId: PropTypes.string,
    displayConfig: PropTypes.object,
    matchedIds: PropTypes.array,
};

ListItemPreviousVersions.defaultProps = {
    matchedIds: [],
};

const component: React.ComponentType<any> = connect()(ListItemPreviousVersions);

export default component;
