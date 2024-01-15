import React, {Fragment} from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';

import {
    toggleNavigation
} from '../../search/actions';
import {gettext} from 'utils';

import {
    fetchItems
} from '../../wire/actions';
import SearchBase from 'layout/components/SearchBase';
import NavigationSixPerRow from 'components/cards/render/NavigationSixPerRow';


class MarketPlaceApp extends SearchBase<any> {
    constructor(props: any) {
        super(props);
    }

    render() {
        const {cards} = this.props;

        return (
            <Fragment>
                <section className="content-main d-block py-4 px-2 p-md-3 p-lg-4">
                    <div className="container-fluid">
                        {get(cards,  'length', 0) > 0 && cards.map(
                            (card: any) => <NavigationSixPerRow key={card._id} card={card}/>
                        )}
                        {get(cards,  'length', 0) === 0 && <div className="alert alert-warning" role="alert">
                            <strong>{gettext('Warning')}!</strong> {gettext('There\'s no navigations defined!')}
                        </div>}
                    </div>
                </section>
                {this.renderSavedItemsCount()}
            </Fragment>
        );
    }
}


MarketPlaceApp.propTypes = {
    user: PropTypes.string,
    company: PropTypes.string,
    navigations: PropTypes.array.isRequired,
    cards: PropTypes.array.isRequired,
    fetchItems: PropTypes.func,
    savedItemsCount: PropTypes.number,
};

const mapStateToProps = (state: any) => ({
    user: state.user,
    company: state.company,
    navigations: get(state, 'navigations', []),
    cards: get(state, 'cards', null),
    savedItemsCount: state.savedItemsCount
});

const mapDispatchToProps = (dispatch: any) => ({
    fetchItems: (navigation: any) => {
        dispatch(toggleNavigation(navigation));
        return dispatch(fetchItems());
    }
});

const component: React.ComponentType<any> = connect(mapStateToProps, mapDispatchToProps)(MarketPlaceApp);

export default component;
