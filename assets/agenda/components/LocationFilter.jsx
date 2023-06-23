import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {get, debounce} from 'lodash';

import {gettext} from 'utils';
import server from 'server';
import {KEYS} from 'common';

import DropdownFilterButton from 'components/DropdownFilterButton';

const LOCATION_TYPE = {
    CITY: 'city',
    STATE: 'state',
    COUNTRY: 'country',
    PLACE: 'location',
};

export class LocationFilter extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            isSearchLoading: false,
            popupOpen: false,
            results: {
                places: [],
                regions: [],
            },
            selectedIndex: -1,
        };
        this.dom = {
            container: null,
            searchInput: null,
            clearButton: null,
        };

        this.toggleDropdown = this.toggleDropdown.bind(this);
        this.handleClickOutside = this.handleClickOutside.bind(this);
        this.handleKeydown = this.handleKeydown.bind(this);
        this.onChange = this.onChange.bind(this);
        this.onSearchInputChange = this.onSearchInputChange.bind(this);
        this.renderRegionSearchResult = this.renderRegionSearchResult.bind(this);

        this.handleSearch = debounce(
            this._handleSearch,
            500,
            {leading: false, trailing: true}
        );
    }

    /**
     * Show or hide the dropdown
     */
    toggleDropdown() {
        if (!this.state.popupOpen) {
            this.showDropdown();
        } else {
            this.hideDropdown();
        }
    }

    /**
     * Show the dropdown, add event listeners and populate list of locations
     */
    showDropdown() {
        document.addEventListener('keydown', this.handleKeydown);
        document.addEventListener('mousedown', this.handleClickOutside);
        this._handleSearch();
        this.setState({popupOpen: true}, () => {
            this.dom.searchInput.focus();
        });
    }

    /**
     * Hide the dropdown, remove event listeners and focus the subnav button
     */
    hideDropdown() {
        document.removeEventListener('keydown', this.handleKeydown);
        document.removeEventListener('mousedown', this.handleClickOutside);
        this.dom.searchInput.value = '';
        this.setState({
            popupOpen: false,
            selectedIndex: -1,
            results: {
                places: [],
                regions: [],
            },
            isSearchLoading: false,
        });

        const parentButton = this.dom.container.querySelector('#subnav_location');

        if (parentButton != null) {
            parentButton.focus();
        }
    }

    /**
     * Hides the dropdown if the mouse was clicked outside
     *
     * @param {MouseEvent} event
     */
    handleClickOutside(event) {
        if (!this.dom.container ||
            this.dom.container.contains(event.target) ||
            !document.contains(event.target) ||
            !this.state.popupOpen
        ) {
            return;
        }

        event.preventDefault();
        event.stopPropagation();
        this.hideDropdown();
    }

    /**
     * Handle keyboard navigation
     *
     * @param {KeyboardEvent} event
     */
    handleKeydown(event) {
        if (event.code === KEYS.ESCAPE) {
            event.preventDefault();
            event.stopPropagation();
            this.toggleDropdown();
            return;
        }

        const activeElement = document.activeElement;
        const numResults = this.state.results.places.length + this.state.results.regions.length;
        const activeIndex = activeElement.getAttribute('data-item-index') != null ?
            parseInt(activeElement.getAttribute('data-item-index'), 10) :
            null;

        if (event.code === KEYS.UP) {
            this.handleKeyUpArrow(event, activeElement, numResults, activeIndex);
        } else if (event.code === KEYS.DOWN) {
            this.handleKeyDownArrow(event, activeElement, numResults, activeIndex);
        } else if (event.code === KEYS.ENTER) {
            this.handleKeyEnter(event, activeElement, numResults, activeIndex);
        }
    }

    /**
     * Handle keyboard navigation: Up Arrow key
     *
     * @param {KeyboardEvent} event
     * @param {Element | null} activeElement - The currently focused DOM element
     * @param {Number} numResults - The number of search results (both regions & places)
     * @param {Number | null} activeIndex - The `data-item-index` attribute of current focused element
     */
    handleKeyUpArrow(event, activeElement, numResults, activeIndex) {
        if (activeElement === this.dom.searchInput) {
            // Place focus on the last item in the search results
            event.preventDefault();
            this.focusItem(numResults - 1);
        } else if (activeElement === this.dom.clearButton) {
            // Place focus on the search input
            event.preventDefault();
            this.dom.searchInput.focus();
        } else if (activeIndex != null) {
            // A search result item is currently focused
            event.preventDefault();
            const itemIndex = activeIndex - 1;

            if (itemIndex < 0) {
                // Place focus on either the 'Any Location' button or the search input
                if (this.dom.clearButton != null) {
                    this.dom.clearButton.focus();
                } else {
                    this.dom.searchInput.focus();
                }
                this.setState({selectedIndex: -1});
            } else {
                // Move focus up one item in the search results
                this.focusItem(itemIndex);
            }
        }
    }

    /**
     * Handle keyboard navigation: Down Arrow key
     *
     * @param {KeyboardEvent} event
     * @param {Element | null} activeElement - The currently focused DOM element
     * @param {Number} numResults - The number of search results (both regions & places)
     * @param {Number | null} activeIndex - The `data-item-index` attribute of current focused element
     */
    handleKeyDownArrow(event, activeElement, numResults, activeIndex) {
        if (activeElement === this.dom.searchInput) {
            // Place focus on either the 'Any Location' button or first item in search results
            event.preventDefault();

            if (this.dom.clearButton != null) {
                this.dom.clearButton.focus();
            } else {
                this.focusItem(0);
            }
        } else if (activeElement === this.dom.clearButton) {
            // Place focus on the first item in the search results
            event.preventDefault();
            this.focusItem(0);
        } else if (activeIndex != null) {
            // A search result item is currently focused
            event.preventDefault();
            const itemIndex = activeIndex + 1;

            if (itemIndex >= numResults) {
                // Place focus on first item, so the list scrolls back to the top
                // Then schedule a task to focus the search input
                this.focusItem(0);
                window.setTimeout(() => {
                    this.dom.searchInput.focus();
                    this.setState({selectedIndex: -1});
                });
            } else {
                // Move focus down one item in the search results
                this.focusItem(itemIndex);
            }
        }
    }

    /**
     * Handle keyboard navigation: Enter key
     *
     * @param {KeyboardEvent} event
     * @param {Element | null} activeElement - The currently focused DOM element
     * @param {Number} numResults - The number of search results (both regions & places)
     * @param {Number | null} activeIndex - The `data-item-index` attribute of current focused element
     */
    handleKeyEnter(event, activeElement, numResults, activeIndex) {
        if (activeElement === this.dom.searchInput && numResults === 1) {
            // If there is only 1 result, then select that one
            event.preventDefault();
            this.onChange(this.state.results.places.length > 0 ?
                this.state.results.places[0] :
                this.state.results.regions[0]
            );
        } else if (activeIndex != null) {
            // If a search result item is currently focused, select that
            event.preventDefault();
            document.querySelector(`[data-item-index="${activeIndex}"]`).click();
        }
    }

    /**
     * Focus an item in the search results, by index
     *
     * @param {Number} index
     */
    focusItem(index) {
        this.setState({selectedIndex: index});
        const item = document.querySelector(`[data-item-index="${index}"]`);

        if (item != null) {
            item.focus();
        }
    }

    /**
     * Select an item to be added to the search filter
     *
     * @param {Object} selected
     */
    onChange(selected) {
        this.toggleDropdown();
        this.props.toggleFilter('location', selected);
    }

    /**
     * Handle changes to the search input text
     *
     * @param {Event} e
     */
    onSearchInputChange(e) {
        this.handleSearch(e.target.value);
    }

    /**
     * Send search query to the server, and save aggregation results in local state
     *
     * @param {String | undefined} query
     * @private
     */
    _handleSearch(query) {
        this.setState({isSearchLoading: true});
        let searchURL = '/agenda/search_locations';

        if (query && query.length) {
            searchURL += `?q=${query}`;
        }

        server.get(searchURL)
            .then((results) => {
                this.setState({
                    isSearchLoading: false,
                    results: results,
                });
            });
    }

    /**
     * Render a search result item for the dropdown menu
     *
     * @param {Object | String} item - The search result item to render
     * @param {Number} index - The index in the results list
     * @returns {JSX.Element}
     */
    renderRegionSearchResult(item, index) {
        const {selectedIndex} = this.state;

        if (item.type === LOCATION_TYPE.CITY) {
            return (
                <button
                    key={`city.${item.name}[${index}]`}
                    data-item-index={index}
                    role="option"
                    aria-selected={index === selectedIndex}
                    className={classNames(
                        'dropdown-item',
                        {active: index === selectedIndex}
                    )}
                    onClick={() => this.onChange(item)}
                >
                    {gettext('{{ name }} (City, {{ state }}, {{ country }})', {
                        name: item.name,
                        state: item.state,
                        country: item.country,
                    })}
                </button>
            );
        } else if (item.type === LOCATION_TYPE.STATE) {
            return (
                <button
                    key={`state.${item.name}[${index}]`}
                    data-item-index={index}
                    role="option"
                    aria-selected={index === selectedIndex}
                    className={classNames(
                        'dropdown-item',
                        {active: index === selectedIndex}
                    )}
                    onClick={() => this.onChange(item)}
                >
                    {gettext('{{ name }} (State, {{ country }})', {
                        name: item.name,
                        country: item.country,
                    })}
                </button>
            );
        } else if (item.type === LOCATION_TYPE.COUNTRY) {
            return (
                <button
                    key={`country.${item.name}[${index}]`}
                    data-item-index={index}
                    role="option"
                    aria-selected={index === selectedIndex}
                    className={classNames(
                        'dropdown-item',
                        {active: index === selectedIndex}
                    )}
                    onClick={() => this.onChange(item)}
                >
                    {gettext('{{ name }} (Country)', {name: item.name})}
                </button>
            );
        } else {
            const results = this.state.results;

            return (
                <button
                    key={`place.${item}[${index}]`}
                    data-item-index={(results.regions.length) + index}
                    role="option"
                    aria-selected={selectedIndex === (results.regions.length) + index}
                    className={classNames(
                        'dropdown-item',
                        {active: selectedIndex === (results.regions.length) + index}
                    )}
                    onClick={() => this.onChange({name: item, type: LOCATION_TYPE.PLACE})}
                >
                    {item}
                </button>
            );
        }
    }

    /**
     * Get the label to use for the subnav filter button
     *
     * @returns {String}
     */
    getFilterLabel() {
        const activeFilter = get(this.props, 'activeFilter.location') || {};

        switch (activeFilter.type) {
        case LOCATION_TYPE.CITY:
            return gettext('City: {{ name }}', {name: activeFilter.name});
        case LOCATION_TYPE.STATE:
            return gettext('State: {{ name }}', {name: activeFilter.name});
        case LOCATION_TYPE.COUNTRY:
            return gettext('Country: {{ name }}', {name: activeFilter.name});
        case LOCATION_TYPE.PLACE:
            return activeFilter.name;
        default:
            return gettext('Any location');
        }
    }

    render() {
        const activeFilter = get(this.props, 'activeFilter.location') || {};
        const isActive = activeFilter.type != null;

        return (
            <div
                key="location"
                className="d-inline-flex position-relative"
                ref={(ref) => this.dom.container = ref}
            >
                <DropdownFilterButton
                    id="subnav_location"
                    icon="icon-small--location"
                    label={this.getFilterLabel()}
                    isActive={isActive}
                    onClick={this.toggleDropdown}
                    autoToggle={false}
                />
                <div
                    className={classNames(
                        'dropdown-menu dropdown-menu-typeahead',
                        {show: this.state.popupOpen}
                    )}
                    aria-labelledby="subnav_location"
                >
                    <div className="d-flex flex-column h-100 d-md-block p-md-2">
                        <div>
                            <input
                                type="text"
                                className="form-control"
                                placeholder={gettext('Search for a region or place')}
                                onChange={this.onSearchInputChange}
                                aria-activedescendant={true}
                                aria-autocomplete="both"
                                aria-expanded={true}
                                aria-haspopup="listbox"
                                aria-owns="dropdown-list-menu"
                                role="combobox"
                                ref={(ref) => this.dom.searchInput = ref}
                            />
                        </div>
                        <div
                            id="dropdown-list-menu"
                            className={classNames(
                                'dropdown-menu dropdown-menu-typeahead overflow-auto',
                                {show: this.state.popupOpen}
                            )}
                        >
                            {!isActive ? null : (
                                <React.Fragment>
                                    <button
                                        type="button"
                                        className="dropdown-item"
                                        onClick={() => this.onChange()}
                                        ref={(ref) => this.dom.clearButton = ref}
                                    >
                                        {gettext('Any location')}
                                    </button>
                                    <div className="dropdown-divider" />
                                </React.Fragment>
                            )}

                            {this.state.isSearchLoading ? (
                                <div className="dropdown-item disabled d-flex">
                                    <div className="spinner-border text-success" />
                                    <span className="ms-3 mt-auto mb-auto">
                                        {gettext('Searching locations...')}
                                    </span>
                                </div>
                            ) : (
                                <React.Fragment>
                                    <h6 className="dropdown-header">{gettext('Regions')}</h6>
                                    {this.state.results.regions.length > 0 ? (
                                        this.state.results.regions.map(this.renderRegionSearchResult)
                                    ) : (
                                        <button
                                            key="empty-regions"
                                            className="dropdown-item disabled"
                                            disabled={true}
                                        >
                                            {gettext('No regions found')}
                                        </button>
                                    )}
                                    <div className="dropdown-divider" />

                                    <h6 className="dropdown-header">{gettext('Places')}</h6>
                                    {this.state.results.places.length > 0 ? (
                                        this.state.results.places.map(this.renderRegionSearchResult)
                                    ) : (
                                        <button
                                            key="empty-places"
                                            className="dropdown-item disabled"
                                            disabled={true}
                                        >
                                            {gettext('No places found')}
                                        </button>
                                    )}
                                </React.Fragment>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

LocationFilter.propTypes = {
    activeFilter: PropTypes.object,
    toggleFilter: PropTypes.func,
};
