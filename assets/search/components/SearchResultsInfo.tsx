import React from 'react';
import PropTypes from 'prop-types';
import 'react-toggle/style.css';
import {connect} from 'react-redux';
import {isEmpty, get} from 'lodash';

import {gettext} from 'utils';

import {
    searchParamsSelector,
} from 'search/selectors';

import NewItemsIcon from './NewItemsIcon';
import {ContentSearchResults} from './ContentSearchResults';

class SearchResultsInfo extends React.Component<any, any> {
    static propTypes: any;
    static defaultProps: any;

    constructor(props: any) {
        super(props);

        this.saveMyTopic = this.saveMyTopic.bind(this);
    }

    saveMyTopic() {
        this.props.saveMyTopic(Object.assign(
            {},
            this.props.activeTopic,
            this.props.searchParams,
            {topic_type: this.props.topicType},
            {filter: get(this.props, 'searchParams.filter', null)})
        );
    }

    render() {
        const activeTopic = get(this.props, 'activeTopic', {});
        const user = get(this.props, 'user', {});
        const saveButtonText = activeTopic._id != null ?
            gettext('Update my topic') :
            gettext('Create my topic');
        const canSaveTopic = !activeTopic._id ||
            !activeTopic.is_global ||
            (
                activeTopic.is_global &&
                user.manage_company_topics === true
            );

        return (
            <ContentSearchResults
                minimizeSearchResults={this.props.minimizeSearchResults}
                showTotalItems={this.props.showTotalItems}
                showTotalLabel={this.props.showTotalLabel}
                showSaveTopic={this.props.showSaveTopic && canSaveTopic}
                totalItems={this.props.totalItems}
                totalItemsLabel={this.props.totalItemsLabel}
                saveMyTopic={this.saveMyTopic}
                saveButtonText={saveButtonText}
                fetchItems={this.props.refresh}
            >
                {isEmpty(this.props.newItems) ? null : (
                    <NewItemsIcon
                        newItems={this.props.newItems}
                        refresh={this.props.refresh}
                    />
                )}
            </ContentSearchResults>
        );
    }
}

SearchResultsInfo.propTypes = {
    user: PropTypes.object,

    minimizeSearchResults: PropTypes.bool,
    showTotalItems: PropTypes.bool,
    showTotalLabel: PropTypes.bool,
    showSaveTopic: PropTypes.bool,

    totalItems: PropTypes.number,
    totalItemsLabel: PropTypes.string,

    saveMyTopic: PropTypes.func,
    searchParams: PropTypes.object,
    activeTopic: PropTypes.object,
    topicType: PropTypes.string,

    newItems: PropTypes.array,
    refresh: PropTypes.func,
};

SearchResultsInfo.defaultProps = {
    minimizeSearchResults: false,
    showTotalItems: true,
    showTotalLabel: true,
    showSaveTopic: false,
};

const mapStateToProps: any = (state: any) => ({
    user: state.userObject,
    searchParams: searchParamsSelector(state),
});

const component: React.ComponentType<any> = connect(mapStateToProps, null)(SearchResultsInfo);

export default component;
