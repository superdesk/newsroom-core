import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {gettext} from 'utils';
import {
    newCard,
    fetchCards,
} from '../actions';
import {setSearchQuery} from 'search/actions';

import Cards from './Cards';
import ListBar from 'components/ListBar';
import DashboardSwitch from 'features/dashboard/DashboardSwitch';


class CardsApp extends React.Component<any, any> {
    static propTypes: any;
    constructor(props: any, context: any) {
        super(props, context);
    }

    render() {
        return (
            [<ListBar
                key="CardBar"
                onNewItem={this.props.newCard}
                setQuery={this.props.setQuery}
                fetch={this.props.fetchCards}
                buttonText={gettext('New Card')}
            >
                <DashboardSwitch
                    dashboards={this.props.dashboards}
                    activeDashboard={this.props.activeDashboard}
                />
            </ListBar>,
            <Cards key="Cards"/>]
        );
    }
}

CardsApp.propTypes = {
    newCard: PropTypes.func,
    fetchCards: PropTypes.func,
    setQuery: PropTypes.func,
    dashboards: PropTypes.array,
    activeDashboard: PropTypes.string,
};

const mapStateToProps = (state: any) => ({
    dashboards: state.dashboards.list,
    activeDashboard: state.dashboards.active,
});

const mapDispatchToProps: any = {
    newCard,
    fetchCards,
    setQuery: setSearchQuery,
};

export default connect(mapStateToProps, mapDispatchToProps)(CardsApp);
