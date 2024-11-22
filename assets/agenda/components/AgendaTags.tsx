import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';

import {gettext, isDisplayed} from 'utils';
import {filterGroupsToLabelMap} from 'search/selectors';

import InfoBox from 'wire/components/InfoBox';
import PreviewTagsBlock from 'wire/components/PreviewTagsBlock';
import {PreviewTagsLinkList} from 'wire/components/PreviewTagsLinkList';
import {PreviewTagsSubjects} from 'wire/components/PreviewTagsSubjects';
import {getSubjects} from '../utils';


function AgendaTagsComponent({item, plan, isItemDetail, displayConfig, filterGroupLabels}: any) {
    const services = !isDisplayed('services', displayConfig) ? null : (
        <PreviewTagsLinkList
            urlPrefix="/agenda?filter="
            items={[...(get(item, 'service') || []), ...(get(plan, 'service') || [])]}
            field="service"
        />
    );

    const subjects = (
        <PreviewTagsSubjects
            subjects={[...getSubjects(item), ...getSubjects(plan)]}
            displayConfig={displayConfig}
            urlPrefix="/agenda?filter="
            filterGroupLabels={filterGroupLabels}
        />
    );

    if (!subjects && !services) {
        return null;
    }

    return (
        <InfoBox
            label={gettext('Metadata')}
            top={!isItemDetail}
        >
            {!services ? null : (
                <PreviewTagsBlock label={get(filterGroupLabels, 'service', gettext('Category'))}>
                    {services}
                </PreviewTagsBlock>
            )}
            {subjects}
        </InfoBox>
    );
}

AgendaTagsComponent.propTypes = {
    item: PropTypes.object,
    plan: PropTypes.object,
    isItemDetail: PropTypes.bool,
    displayConfig: PropTypes.object,
    filterGroupLabels: PropTypes.object,
};

const mapStateToProps = (state: any) => ({
    filterGroupLabels: filterGroupsToLabelMap(state),
});

const AgendaTags: React.ComponentType<any> = connect(mapStateToProps)(AgendaTagsComponent);

export default AgendaTags;
