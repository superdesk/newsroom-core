import React from 'react';
import {gettext} from 'assets/utils';

export class SearchBar extends React.PureComponent<any, any> {
    constructor(props: any) {
        super(props);
        this.state = {value: ''};
    }

    render() {
        return (
            <section className="content-header">
                <nav className="content-bar navbar justify-content-start flex-nowrap flex-sm-wrap">
                    <div className="search d-flex align-items-center">
                        <span className="search__icon d-none d-sm-block">
                            <i className="icon--search icon--gray" />
                        </span>
                        <div className="search__form input-group searchForm--active">
                            <form className="d-flex align-items-center" action="/wire" role="search" aria-label={gettext('search')}>
                                <input type="text" name="q" className="search__input form-control"
                                    placeholder={gettext('Search for...')}
                                    aria-label={gettext('Search for...')}
                                    onChange={(event) => this.setState({value: event.target.value})}
                                />
                                <div className="search__form__buttons">
                                    {this.state.value && (
                                        <button type="reset" className="icon-button search__clear" title={gettext('Clear')}>
                                            <span className="search__clear">
                                                <img src="/static/search_clear.png" width="16" height="16"/>
                                            </span>
                                        </button>
                                    )}
                                    <button className="btn btn-outline-secondary" type="submit" title={gettext('Search')}>
                                        {gettext('Search')}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </nav>
            </section>
        );
    }
}
