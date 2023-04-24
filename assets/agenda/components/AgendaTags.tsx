import {filterGroupsToLabelMap} from 'assets/search/selectors';
import {gettext, isDisplayed} from 'assets/utils';
import InfoBox from 'assets/wire/components/InfoBox';
import PreviewTagsBlock from 'assets/wire/components/PreviewTagsBlock';
import {PreviewTagsLinkList} from 'assets/wire/components/PreviewTagsLinkList';
import {PreviewTagsSubjects} from 'assets/wire/components/PreviewTagsSubjects';
import {get} from 'lodash';
import PropTypes from 'prop-types';
import React from 'react';
import {connect} from 'react-redux';
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
            label={isItemDetail ? gettext('Metadata') : null}
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

const AgendaTags = connect(mapStateToProps)(AgendaTagsComponent);

export default AgendaTags;
