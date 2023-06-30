import React from 'react';
import { NavLink } from 'react-router-dom';
//import { useNavigate } from 'react-router-dom';

function Home() { 
    const items = [
        { path: '/', title: 'Home' },
        { path: '/settings', title: 'Settings' },
        { path: '/wire', title: 'Wire' },
    ];
    
    return (
        <div id="home-app" className="content">
            <section className="content-main d-block py-4 px-2 p-md-3 p-lg-4">
                <div className="home-tools">
                    <button type="button" className="nh-button nh-button--secondary nh-button--small" title="Personalize Home">Personalize Home</button>
                </div>
                <div className="text-color--muted text-center font-size--medium py-2"><span className="text-color--default">Note: </span> The block below apperas if there already is a personal home/dashboard:</div>
                <div className="home-tools">
                    <div className="toggle-button__group">
                        <button className="toggle-button toggle-button--small toggle-button--active">Default</button>
                        <button className="toggle-button toggle-button--small">My Home</button>
                    </div>
                    <button type="button" className="icon-button icon-button--small icon-button--tertiary icon-button--bordered" title="Edit personal Home">
                        <i className="icon--settings"></i>
                    </button>
                </div>
                <div className="container-fluid">
                    <div className="row">
                        <div className="home-section__header">
                            <h3 className="home-section__title">Alberta</h3>
                            <button type="button" className="nh-button nh-button--tertiary nh-button--small" title="More News">More News</button>
                        </div>
                        <div className="col-sm-6 col-md-4 col-lg-3 col-xxl-2 d-flex mb-4">
                            <div className="card card--home">
                                <div className="card-body">
                                    <h4 className="card-title">Jonathan Marchessault scores 3 to lead Golden Knights past Oilers 5-2 to advance to West final</h4>
                                    <div className="wire-articles__item__text">
                                        <p className="card-text small">
                                            Jonathan Marchessault scored three goals for his second career postseason hat trick as the 
                                            Vegas Golden Knights beat the Edmonton Oilers 5-2 in Game 6 of their second-round series to
                                            advance to the Western Conference final. Reilly Smith and William...
                                        </p>
                                    </div>
                                </div>
                                <div className="card-footer">
                                    <div className="wire-articles__item__meta">
                                        <div className="wire-articles__item__icons">
                                            <span className="wire-articles__item__icon">
                                                <i className="icon--text icon--gray-dark"></i>
                                            </span>
                                        </div>
                                        <div className="wire-articles__item__meta-info">
                                            <span>The Associated Press<span>  //  <span>865</span> words</span> // <time dateTime="08:49 May 15th, 2023">May 15th, 2023</time></span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col-sm-6 col-md-4 col-lg-3 col-xxl-2 d-flex mb-4">
                            <div className="card card--home">
                                <div className="card-body">
                                    <h4 className="card-title">Rothesay International Results</h4>
                                    <div className="wire-articles__item__text">
                                        <p className="card-text small">
                                            Wednesday At Devonshire Park Lawn Tennis Club Eastbourne, Great Britain Purse: €723,655 
                                            Surface: Grass EASTBOURNE, GREAT BRITAIN (AP) _ Results Wednesday from Rothesay International 
                                            at Devonshire Park Lawn Tennis Club (seedings in parentheses): Men's Singles Round of 16 Miomir Kecmanovic...
                                        </p>
                                    </div>
                                </div>
                                <div className="card-footer">
                                    <div className="wire-articles__item__meta">
                                        <div className="wire-articles__item__icons">
                                            <span className="wire-articles__item__icon">
                                                <i className="icon--text icon--gray-dark"></i>
                                            </span>
                                        </div>
                                        <div className="wire-articles__item__meta-info">
                                            <span>The Associated Press<span>  //  <span>121</span> words</span> // <time dateTime="15:04 May 20th, 2023">May 20th, 2023</time></span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col-sm-6 col-md-4 col-lg-3 col-xxl-2 d-flex mb-4">
                            <div className="card card--home">
                                <div className="card-body">
                                    <h4 className="card-title">Nugent-Hopkins has goal, assist to help Oilers beat Golden Knights 4-1, even series at 2-2</h4>
                                    <div className="wire-articles__item__text">
                                        <p className="card-text small">
                                            Ryan Nugent-Hopkins had a goal and an assist as the Edmonton Oilers beat the Vegas Golden 
                                            Knights 4-1 to even their second-round playoff series at two games apiece. Nick Bjugstad, 
                                            Evan Bouchard and Mattias Ekholm also scored as the Oilers...
                                        </p>
                                    </div>
                                </div>
                                <div className="card-footer">
                                    <div className="wire-articles__item__meta">
                                        <div className="wire-articles__item__icons">
                                            <span className="wire-articles__item__icon">
                                                <i className="icon--text icon--gray-dark"></i>
                                            </span>
                                        </div>
                                        <div className="wire-articles__item__meta-info">
                                            <span>The Associated Press<span>  //  <span>459</span> words</span> // <time dateTime="12:23 May 18th, 2023">May 18th, 2023</time></span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col-sm-6 col-md-4 col-lg-3 col-xxl-2 d-flex mb-4">
                            <div className="card card--home">
                                <div className="card-body">
                                    <h4 className="card-title">Marchessault, Eichel lead Vegas to 5-1 win over Oilers</h4>
                                    <div className="wire-articles__item__text">
                                        <p className="card-text small">
                                            Jonathan Marchessault scored his first two goals of the playoffs, Jack Eichel had a goal 
                                            and an assist, and the Vegas Golden Knights beat the Edmonton Oilers 5-1 for a 2-1 lead 
                                            in their second-round playoff series. Zach Whitecloud and...
                                        </p>
                                    </div>
                                </div>
                                <div className="card-footer">
                                    <div className="wire-articles__item__meta">
                                        <div className="wire-articles__item__icons">
                                            <span className="wire-articles__item__icon">
                                                <i className="icon--text icon--gray-dark"></i>
                                            </span>
                                        </div>
                                        <div className="wire-articles__item__meta-info">
                                            <span>The Associated Press<span>  //  <span>289</span> words</span> // <time dateTime="15:27 May 15th, 2023">May 15th, 2023</time></span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col-sm-6 col-md-4 col-lg-3 col-xxl-2 d-flex mb-4">
                            <div className="card card--home">
                                <div className="card-body">
                                    <h4 className="card-title">Arizona's Oak Flat is sacred land to some Native Americans but proposed as a giant copper miner</h4>
                                    <div className="wire-articles__item__text">
                                        <p className="card-text small">
                                            Oak Flat, a mountainous area east of Phoenix, is an Apache sacred site where Native 
                                            Americans gather to pray and perform coming-of-age ceremonies and sweat rituals. A 
                                            multinational corporation has proposed a massive copper mine on the flats, which could...
                                        </p>
                                    </div>
                                </div>
                                <div className="card-footer">
                                    <div className="wire-articles__item__meta">
                                        <div className="wire-articles__item__icons">
                                            <span className="wire-articles__item__icon">
                                                <i className="icon--text icon--gray-dark"></i>
                                            </span>
                                        </div>
                                        <div className="wire-articles__item__meta-info">
                                            <span>The Associated Press<span>  //  <span>326</span> words</span> // <time dateTime="12:24 May 15th, 2023">May 15th, 2023</time></span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col-sm-6 col-md-4 col-lg-3 col-xxl-2 d-flex mb-4">
                            <div className="card card--home">
                                <div className="card-body">
                                    <h4 className="card-title">Space Disco Cowboy? Couples ditch traditional dress codes in favor of out-there themes</h4>
                                    <div className="wire-articles__item__text">
                                        <p className="card-text small">
                                            Space disco cowboy. Yacht Shabbat. Burning Man Formal. Dress to Express Your Inner Spirit. 
                                            More bridal couples are tossing tradition when it comes to what guests should wear. Summer 
                                            is a busy wedding season. For some guests, that means boomeranging...
                                        </p>
                                    </div>
                                </div>
                                <div className="card-footer">
                                    <div className="wire-articles__item__meta">
                                        <div className="wire-articles__item__icons">
                                            <span className="wire-articles__item__icon">
                                                <i className="icon--text icon--gray-dark"></i>
                                            </span>
                                        </div>
                                        <div className="wire-articles__item__meta-info">
                                            <span>The Associated Press<span>  //  <span>6</span> words</span> // <time dateTime="10:36 May 15th, 2023">May 15th, 2023</time></span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>   
        
    );
}

export default Home;