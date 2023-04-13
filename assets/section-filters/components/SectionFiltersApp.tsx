import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import ListBar from 'assets/components/ListBar';
import SectionSwitch from 'assets/features/sections/SectionSwitch';
import {sectionsSelector, activeSectionSelector} from 'assets/features/sections/selectors';
import {sectionsPropType} from 'assets/features/sections/types';
import {setSearchQuery} from 'assets/search/actions';
import {gettext} from 'assets/utils';
import {fetchSectionFilters, newSectionFilter} from '../actions';
import SectionFilters from './SectionFilters';

class SectionFiltersApp extends React.Component<any, any> {
    static propTypes: any;
    constructor(props: any, context: any) {
        super(props, context);
    }

    render() {
        return [
            <ListBar key="bar"
                onNewItem={this.props.newSectionFilter}
                setQuery={this.props.setQuery}
                fetch={this.props.fetchSectionFilters}
                buttonText={gettext('New Section Filter')}
            >
                <SectionSwitch
                    sections={this.props.sections}
                    activeSection={this.props.activeSection}
                />
            </ListBar>,
            <SectionFilters
                key="sectionFilters"
                activeSection={this.props.activeSection}
                sections={this.props.sections} />
        ];
    }
}

SectionFiltersApp.propTypes = {
    sections: sectionsPropType,
    activeSection: PropTypes.string.isRequired,

    fetchProducts: PropTypes.func,
    setQuery: PropTypes.func,
    newSectionFilter: PropTypes.func,
    fetchSectionFilters: PropTypes.func,
};

const mapStateToProps = (state: any) => ({
    sections: sectionsSelector(state),
    activeSection: activeSectionSelector(state),
});

const mapDispatchToProps = {
    fetchSectionFilters,
    setQuery: setSearchQuery,
    newSectionFilter,
};

export default connect(mapStateToProps, mapDispatchToProps)(SectionFiltersApp);
