import React from 'react';
import {get} from 'lodash';
import NavigationCard from './NavigationCard';


function NavigationSixPerRow({card}: any) {
    const navigations = get(card, 'config.navigations') || [];

    const cards = navigations.map((nav: any) => (
        <NavigationCard
            navigation={nav}
            key={nav._id}
        />
    ));

    if (get(cards, 'length', 0) === 0) {
        return null;
    }

    return (
        <div className="row">
            <div className="col-12 col-sm-12">
                <h3 className="home-section-heading">{card.label}</h3>
            </div>
            {cards}
        </div>
    );
}

export default NavigationSixPerRow;
